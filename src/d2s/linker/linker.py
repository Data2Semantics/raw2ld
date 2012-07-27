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
from pprint import pprint
from urllib import quote

plugin.register('sparql', query.Processor,
               'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', query.Result,
               'rdfextras.sparql.query', 'SPARQLQueryResult')


class Linker(object):
    
    # Eculture
    FULL_SPARQL_ENDPOINT = "http://eculture2.cs.vu.nl:5020/sparql/"
    # Local
    LOCAL_SPARQL_ENDPOINT = "http://localhost:8000/sparql/"
    
    AERS_SPARQL_ENDPOINT = FULL_SPARQL_ENDPOINT
    
    aers_wrapper = SPARQLWrapper(AERS_SPARQL_ENDPOINT)
    lld_wrapper = SPARQLWrapper("http://linkedlifedata.com/sparql")
    
    g = ConjunctiveGraph()
    
    def __init__(self):
        # Setup SPARQLWrappers for AERS-LD and LLD
        self.aers_wrapper.setReturnFormat(JSON)
        self.aers_wrapper.addCustomParameter('soft-limit','-1')
        
        self.lld_wrapper.setReturnFormat(JSON)
        
        # Define Namespaces
        self.AERS = Namespace("http://aers.data2semantics.org/resource/")
        self.DBPEDIA = Namespace("http://dbpedia.org/resource/")
        self.SIDER = Namespace("http://www4.wiwiss.fu-berlin.de/sider/resource/sider/")
        self.OWL = Namespace("http://www.w3.org/2002/07/owl#")
        self.SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
        
        # Setup Graph
        self.g.bind("aers", "http://aers.data2semantics.org/resource/")
        self.g.bind("dbpedia", "http://dbpedia.org/resource/")
        self.g.bind("owl", "http://www.w3.org/2002/07/owl#")
        self.g.bind("sider", "http://www4.wiwiss.fu-berlin.de/sider/resource/sider/")
        self.g.bind("skos","http://www.w3.org/2004/02/skos/core#")
    
    

    def unique_list(self,l):
        ulist = []
        [ulist.append(x) for x in l if x not in ulist]
        return ulist
            
    def doQuery(self, sparql, query, name=''):
        sparql.setQuery(query)
        print "Starting query {0}...".format(name)
    #    print query
        
        tstart = time()
        res = sparql.query().convert()
        tend = time()
        print "... done ({0}us)".format(tend-tstart)
        resultsno = len(res["results"]["bindings"])
        print "Query returned {0} results.".format(resultsno)
        
        return res
    
    def createIndex(self, res, label_index = {}, reverse_uri_index = {}, labelFunction=None, regex=None):
        # Create Index
        for result in res["results"]["bindings"]:
            uri = result["resource"]["value"]
            if labelFunction == None :
                label = result["label"]["value"].strip().lower()
            else :
                if regex == None :
                    exec 'label ='+labelFunction+'("'+result["label"]["value"]+'").strip().lower()'
                else :
                    exec 'label ='+labelFunction+'("'+result["label"]["value"]+'","'+regex+'").strip().lower()'
            
#            keylist = [s for s in re.split(r'\s+|\/|\+|\D\.\D|,|\(|\)|\[|\]|\'|\"|\-|\_|\\|\^',label) if s != '']
#            key = " ".join(keylist)
            
#            print "In:  {}".format(label)
            label_normalized = self.normalizeLabel(label)
#            print "Out: {}".format(label_normalized)
            
            
            # Replace spaces with underscores
            uri_normalized = re.sub(r'\.|\,',r'',label_normalized)
            uri_normalized = re.sub(r'\s+','_',uri_normalized)
            uri_normalized = quote(uri_normalized)
            
            nuri = "http://aers.data2semantics.org/resource/drug/{}".format(uri_normalized)
            
            if label_normalized != label :
                print "Old: '{}'\nNew: '{}'".format(label, label_normalized)
#                print "OldURI: {}\nNewURI: {}".format(uri,nuri)
            
            label_index.setdefault(label_normalized,{})
            label_index[label_normalized].setdefault('uri',nuri)
            label_index[label_normalized].setdefault('resources', []).append({"label": label, "uri": uri})
            
            reverse_uri_index[uri] = nuri
        
        return label_index, reverse_uri_index
    
    def normalizeLabel(self, label):
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
        label_normalized = re.sub(r'\)\(',') (',label_normalized)
        label_normalized = re.sub(r'(\w)\(',r'\1 (',label_normalized)
        label_normalized = re.sub(r'\)(\w)',r'( \1',label_normalized)
        label_normalized = re.sub(r'\((\w+)\(',r'(\1)',label_normalized)
        label_normalized = re.sub(r'(\s|(\,\s*))\)',r')',label_normalized)
        label_normalized = re.sub(r'^\((.*?)\)',r'\1',label_normalized)
        
        # Remove duplicates
        label_normalized = re.sub(r'(\w{3,}) \1',r'\1',label_normalized)
        label_normalized = re.sub(r'(\w{3,})(.*?)\(\1\)',r'\1\2',label_normalized)
        label_normalized = re.sub(r'(\w{3,}(\s\w{3,})+)(.*?)\(\1\)',r'\1\3',label_normalized)
        

        
        
        # Also remove partial duplicates that were cut off at the end of the string
        label_normalized = re.sub(r'(\w{3,})(.*?)\(\1$',r'\1\2',label_normalized)
        
        # Add missing brackets
        label_normalized = re.sub(r'\(((\w|\s|\,)+)$',r'(\1)',label_normalized)
        
        label_normalized = re.sub(r'\s+',' ',label_normalized)
        label_normalized = label_normalized.strip()
            
        return label_normalized
    
    def crossLink(self, label_index):
        uri_narrowers = {}
#        index = {"a": ["a"], "a b": ["a b"], "a b c": ["a b c"], "c": ["c"], "b c": ["b c"]}
        
        for current_label in label_index :
            # Initialise the 'broaders' key in the dictionary as a list
            label_index[current_label].setdefault('narrowers',[])
            uri_narrowers.setdefault(label_index[current_label]['uri'],[])
            # Split the label by space
            lsplit = [s for s in re.split(r'\s+|\/|\+|,|\(|\)|\"',current_label) if (s != '' and len(s)>2)]

#            print lsplit
            
#            print "======================================"
            visited = []
            for step in range(1,4) :
                for start in range(len(lsplit)) :
                    end = len(lsplit)
                    for i in range(start,end):
                        if i+step <= end and not (i,i+step) in visited:
                            visited.append((i,i+step))
                            partial_label = " ".join(lsplit[i:i+step])
                            
                            # If the partial_label is a normalized label of an actual (known) resource
                            # We add that known resource to the broaders of the resource with the current_label
                            if partial_label in label_index and (partial_label != current_label) :

                                label_index[current_label]['narrowers'].append({'label': partial_label, 'uri': label_index[partial_label]['uri']})
                                uri_narrowers.setdefault(label_index[partial_label]['uri'],[]).append(label_index[current_label]['uri'])

                                print "'{}' is narrower than '{}'".format(current_label, partial_label) 
                                
        
        return label_index, uri_narrowers
        
        





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--drugs", help="Link drugs", action="store_true")
    parser.add_argument("--diagnoses", help="Link diagnoses", action="store_true")
    parser.add_argument("--countries", help="Link countries", action="store_true")
    args = parser.parse_args()
    
    l = Linker()
    q = Queries()
    
    drugResultsFile = "aers_drugs_results.pickle"
    
    if os.path.exists(drugResultsFile) :
        print "Loading from pickle"
        aers_drugs_results = pickle.load(open(drugResultsFile,"r"))
    else :
        aers_drugs_results = l.doQuery(l.aers_wrapper, q.aers_drug)
        pickle.dump(aers_drugs_results, open(drugResultsFile,"w"))
    
    print "Creating index"
    label_index, reverse_uri_index = l.createIndex(aers_drugs_results)
    print "done"
    print "Starting to crosslink"
    label_index, uri_narrowers = l.crossLink(label_index)
    print "done"
#    pprint(index)
#    pprint(narrowers)
    
    count = 0
    for key in label_index:
        count += len(label_index[key]['narrowers'])
#            print "{}\t->\t{} ({})".format(label_index[key]['uri'],n['uri'],n['label'])
        
    
    print "Results", len(aers_drugs_results["results"]["bindings"])
    print "Index  ", len(label_index)
    print "Delta  ", len(aers_drugs_results["results"]["bindings"]) - len(label_index)
    print "Number of broader relations", count
    
    reverseURIFile = "reverse_uri_index.pickle"
    pickle.dump(reverse_uri_index, open(reverseURIFile,'w'))
    
    indexFile = "aers_drugs_index.pickle"
    pickle.dump(label_index, open(indexFile,'w'))

    narrowersFile = "aers_drugs_narrowers.pickle"
    pickle.dump(uri_narrowers, open(narrowersFile,'w'))
    