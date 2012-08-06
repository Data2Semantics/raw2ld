'''
Created on Jul 17, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON, XML
from time import time
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, plugin, query
#from d2s.prov import Trace
from queries import Queries
import argparse
import os.path
import pickle
from urllib import quote, unquote
import yaml

plugin.register('sparql', query.Processor,
               'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', query.Result,
               'rdfextras.sparql.query', 'SPARQLQueryResult')




class Linker(object):
    

    
    def __init__(self, prefixes):
        self.prefixes = prefixes
        return
    

    def unique_list(self,l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist]
        return ulist
            
    def doQuery(self, endpoint, query, name=''):
        sparql = SPARQLWrapper(endpoint)
        sparql.setReturnFormat(JSON)
        sparql.addCustomParameter('soft-limit', '-1')
        sparql.setQuery(self.prefixes+"\n\n"+query)
        print "Starting query {0}...".format(name)

        tstart = time()
        res = sparql.query().convert()
        tend = time()
        print "... done ({0}us)".format(tend-tstart)
        resultsno = len(res["results"]["bindings"])
        print "Query returned {0} results.".format(resultsno)
        
        return res
    
    def index(self, res, label_index = {}, exact_index = {}, normalized_index = {}, uri_index = {}, normalize = True, prefix = '', labelFunction=None, regex=None):
        # Input is a SPARQL result set with two variables 'resource' and 'label'
        # We create an index where a normalised /label/ is key, and the value is a dictionary of the list of resources, and a normalised uri.
        for (uri,rawlabel) in res:
            rawlabel = rawlabel.encode('utf-8').strip().lower()
            if labelFunction == None :
                label = rawlabel
            else :
                if regex == None :
                    exec 'label = self.'+labelFunction+'("'+rawlabel+'")'
                else :
                    exec 'label = self.'+labelFunction+'("'+rawlabel+'","'+regex+'")'
            

            if normalize :
                # Remove unneeded characters/duplicates from the label.
                label_normalized, qname_normalized = self.normalize(label)
    
                # Mint a URI using the QName
                normalized_uri = prefix + qname_normalized
            else :
                label_normalized = label
                normalized_uri = uri
                        
            # Add the the label as key to the index, setting the value to an empty set (if not already set)
            # Then add the UTF-8 encoded raw label
            label_index.setdefault(label_normalized,set()).add(rawlabel)
            
            exact_index.setdefault(label_normalized,set()).add(normalized_uri)            
            
            uri_index.setdefault(normalized_uri,set()).add(label_normalized)
            
            if normalize:
                # The original_to_normalized_uri_index gives for every original URI, the normalized URI.
                normalized_index[uri] = normalized_uri
        
        # @todo check return format
        return label_index, exact_index, normalized_index, uri_index

    
    def normalize(self, label):
        label_normalized = re.sub(r'\s+',' ',label).strip()

        # Remove /12345678/ thingies
        label_normalized = re.sub(r'\/\s?\d{8}\s?(\/|$)',r'',label_normalized)
        
        label_normalized = re.sub(r'\\','',label_normalized)
        label_normalized = re.sub(r'\s\/\s',' ',label_normalized)
        label_normalized = re.sub(r'\^','',label_normalized)
        label_normalized = re.sub(r'\,$','',label_normalized)
        label_normalized = re.sub(r'\s+\,',',',label_normalized)
        label_normalized = re.sub(r'\,(\w)',r', \1',label_normalized)
        
        # Fix blockbrackets
        label_normalized = re.sub(r'\[','(',label_normalized)
        label_normalized = re.sub(r'\]',')',label_normalized)
        
        # Fix other brackets
        label_normalized = re.sub(r'\(\)','',label_normalized)
        label_normalized = re.sub(r'\(\s','(',label_normalized)
        label_normalized = re.sub(r'\s\)',')',label_normalized)
        label_normalized = re.sub(r'\)\(',') (',label_normalized)
        label_normalized = re.sub(r'(\w)\(',r'\1 (',label_normalized)
        label_normalized = re.sub(r'\)(\w)',r'( \1',label_normalized)
        label_normalized = re.sub(r'\((\w+)\(',r'(\1)',label_normalized)
        label_normalized = re.sub(r'(\s|(\,\s*))\)',r')',label_normalized)
        label_normalized = re.sub(r'^\((.*?)\)',r'\1',label_normalized)
        
        # Remove duplicates
        label_normalized = re.sub(r'(\w{3,}) \1\s',r'\1',label_normalized)
        label_normalized = re.sub(r'(\w{3,})(.*?)\(\1\)',r'\1\2',label_normalized)
        label_normalized = re.sub(r'(\w{3,}(\,?\s\w{3,})+)(.*?)\(\1\)',r'\1\3',label_normalized)
        
        # Also remove partial duplicates that were cut off at the end of the string
        label_normalized = re.sub(r'(\w[\w\s\,]{2,})(.*?)\(\1$',r'\1\2',label_normalized)
        # The same, but when the two duplicates are separated by a forward slash
        label_normalized = re.sub(r'(\w[\w\s\,]{2,})(.*?)\/\1$',r'\1\2',label_normalized)
        # The same, but only if the first string was between brackets
        label_normalized = re.sub(r'\((.{3,})(.+?)\)(.*)\(\1$',r'(\1\2)\3',label_normalized)
        
        # Add missing brackets
        label_normalized = re.sub(r'\(([\w\s\,\/]+)$',r'(\1)',label_normalized)
        
        label_normalized = re.sub(r'\s+',' ',label_normalized)
        label_normalized = label_normalized.strip().encode('utf-8')
            
        # Replace spaces with underscores
        qname_normalized = re.sub(r'\.|\,',r'',label_normalized)
        qname_normalized = re.sub(r'\s+','_',qname_normalized)
        
        qname_normalized = quote(qname_normalized)

            
        return label_normalized, qname_normalized
    
    def related(self, exact_index, related_index={}):
        for current_label in exact_index :
            for resource in exact_index[current_label] :
                related_index.setdefault(resource,set()).update([r for r in exact_index[current_label]])
            
        return related_index
    
    
    
    def broader(self, exact_index):
        # This dictionary will map a URI (the key) to a list of URIs of concepts that are /more general/ than the key.
        uri_broaders = {}
        # Count the number of narrower relations found
        count = 0
        
        for current_label in exact_index :
            # Initialize an entry in the uri_broaders index for all uris related to the current label
            for resource in exact_index[current_label] :
                uri_broaders.setdefault(resource,set())
            
            # Turn the label into a list of words
            label_as_words = [s for s in re.split(r'\s+|\/|\+|,|\(|\)|\"',current_label) if (s != '' and len(s)>2)]

            # Look for other labels that match from 1 to 4 consecutive words in the current label.
            for word_range in range(1,4) :
                # Start at the first word, then check for all words in the label_as_words list. 
                end = len(label_as_words)
                for start in range(end) :
                    # If the starting position + the word range does not exceed the word list
                    if start+word_range <= end :
                        # Create a new partial label, based on the words in label_as_words from start to start+word_range
                        partial_label = " ".join(label_as_words[start:start+word_range])
                        
                        # If the partial_label is a normalized label of an actual (known) resource
                        # We add that known resource to the broaders of the resource with the current_label
                        if partial_label in exact_index and (partial_label != current_label) :
                            for resource in exact_index[current_label]:
                                uri_broaders[resource].update(exact_index[partial_label])
                            
                            count += 1
                                
        
        return uri_broaders, count
        
        


    def getResults(self, endpoint, query, resultsFile):
        results = []
        
        if os.path.exists(resultsFile):
            print "Loading from {}".format(resultsFile)
            results = pickle.load(open(resultsFile, "r"))
            print "done"
        else:
            print "SPARQL Query:"
            print query
            sparql_results = self.doQuery(endpoint, query)
            
            for res in sparql_results["results"]["bindings"] :
                try :
                    results.append((res["resource"]["value"],res["label"]["value"]))
                except :
                    print "SPARQL Query should return two variables 'resource' and 'label'"
                    quit()
            
            print "Dumping results to {}".format(resultsFile)
            pickle.dump(results, open(resultsFile, "w"))
            print "done"
        return results
    
    
    
    def do(self, config):
        print "Starting"
        normalizedFile = config['normalized']
        relatedFile = config['related']
        indexFile = config['labelindex']
        broaderFile = config['broader']
        uriFile = config['uriindex']
        exactFile = config['exact']
        
        

        
        label_index = {}
        normalized_index = {}
        exact_index = {}
        results_count = 0
        print "Building Index"
        for q in config['queries'] :
            name = q['name']
            resultsFile = q['results']
            query = "SELECT DISTINCT ?resource ?label WHERE {\n"+q['pattern']+"}"
            normalize = q['normalize']
            endpoint = q['endpoint']
            if normalize:
                prefix = q['prefix']
            else:
                prefix = ''
            
            print "Running {} on {} (Normalize is {})".format(name, endpoint, normalize)

            if 'labelfunction' in q and 'regex' in q:
                labelFunction = q['labelfunction']
                regex = q['regex']
                print "Using label function {} with regex {}".format(labelFunction, regex)
            else:
                labelFunction = None
                regex = None
            
            results = self.getResults(endpoint, query, resultsFile)
            results_count += len(results)
            
            print "Indexing {}".format(name)
            label_index, exact_index, normalized_index, uri_index = self.index(results, label_index, exact_index, normalized_index, normalize=normalize, prefix=prefix, labelFunction=labelFunction, regex=regex)
            print "done"
        print "Index phase complete"
        
        print "Creating related index"
        related_index = self.related(exact_index)
        print "done"
        
        print "Creating broader index"
        uri_broaders, count = self.broader(exact_index)
        print "done"
        
        print "Results", results_count
        print "Index  ", len(label_index)
        print "Delta  ", results_count - len(label_index)
        print "Number of narrower relations", count
        
        print "Dumping to {}".format(normalizedFile)
        pickle.dump(normalized_index, open(normalizedFile, 'w'))
        print "Dumping to {}".format(exactFile)
        pickle.dump(exact_index, open(exactFile, 'w'))
        print "Dumping to {}".format(relatedFile)
        pickle.dump(related_index, open(relatedFile, 'w'))
        print "Dumping to {}".format(indexFile)
        pickle.dump(label_index, open(indexFile, 'w'))
        print "Dumping to {}".format(uriFile)
        pickle.dump(uri_index, open(uriFile, 'w'))
        print "Dumping to {}".format(broaderFile)
        pickle.dump(uri_broaders, open(broaderFile, 'w'))
        
    
    def slashURIToLabel(self, uri,regex):
        try :
            m = re.search(regex + r'(.*)$', unquote(uri))
            label = m.group(1).replace('_',' ') 
            
#            print uri + " -> " + label
            return label
        except :
            return uri



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="YAML Configuration file")
    parser.add_argument("--drug", help="Link drugs", action="store_true")
    parser.add_argument("--diagnosis", help="Link diagnoses", action="store_true")
    parser.add_argument("--country", help="Link countries", action="store_true")

    args = parser.parse_args()
    
    config = yaml.load(open(args.config, "r"))
    
    
        
    l = Linker(config['prefixes'])

    
    
    if args.drug :
        l.do(config['drug'])
        
    if args.diagnosis :
        l.do(config['diagnosis'])
        
    print "DONE!"



    