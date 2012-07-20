'''
Created on Jul 17, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON, XML
from time import time
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, plugin, query
from d2s.prov import Trace
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
    
    def createIndex(self, res, index, labelFunction=None, regex=None):
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
            
            keylist = [s for s in re.split(r'\s+|\/|\+|\.|,|\(|\)|\[|\]|\'|\"|\-|\_|\\|\^',label) if s != '']
            key = " ".join(keylist)
            
            label_normalized = re.sub(r'\s+',' ',label).strip()
            

#            label_normalized =' '.join(self.unique_list(label_normalized.split(' ()[]^')))
            label_normalized = re.sub(r'\\','',label_normalized)
            label_normalized = re.sub(r'\s\/\s','\s',label_normalized)
            label_normalized = re.sub(r'\^','',label_normalized)
            label_normalized = re.sub(r'\,',' ',label_normalized)
            label_normalized = re.sub(r'\.',' ',label_normalized)
            
            # Fix brackets
            label_normalized = re.sub(r'\[','(',label_normalized)
            label_normalized = re.sub(r'\]',')',label_normalized)
            label_normalized = re.sub(r'\(\)','',label_normalized)
            label_normalized = re.sub(r'\)\(',') (',label_normalized)
            label_normalized = re.sub(r'(\w)\(',r'\1 (',label_normalized)
            label_normalized = re.sub(r'\)(\w)',r'( \1',label_normalized)
            label_normalized = re.sub(r'\((\w+)\(',r'(\1)',label_normalized)
            
            # Remove duplicates
            label_normalized = re.sub(r'(\w+) \1',r'\1',label_normalized)
            label_normalized = re.sub(r'(\w+)(.*?)\(\1\)',r'\1\2',label_normalized)
            
            # Rewrite /28374/ thingies
            label_normalized = re.sub(r'\s?\/\s?(\d+?)\s?(\/|$)',r' /\1/',label_normalized)
            
            # Replace spaces with underscores
            label_underscore = re.sub(r'\s+','_',label_normalized.strip())
            uri_fragment_normalized = quote(label_underscore)
            
            
            
            nuri = "http://aers.data2semantics.org/resource/drug/{}".format(uri_fragment_normalized)
            index.setdefault(key, []).append({"label": label, "uri": uri, "nuri": nuri})
        
        return index
    
    
    def crossLink(self, index):
        narrowers = {}
#        index = {"a": ["a"], "a b": ["a b"], "a b c": ["a b c"], "c": ["c"], "b c": ["b c"]}
        
        for key in index :
            lsplit = re.split(r'\s',key)
            
#            print "======================================"
            visited = []
            for step in range(1,4) :
                for start in range(len(lsplit)) :
                    end = len(lsplit)
                    for i in range(start,end):
                        if i+step <= end and not (i,i+step) in visited:
                            visited.append((i,i+step))
                            l = " ".join(lsplit[i:i+step])
#                            print "{} ({}-{}, {}): {} ({})".format(lsplit, i, i+step, step, l, start)
#                            print "{}: {}".format(key, l)
                            if l in index and (l != key) :
                                narrowers[l] = index[key]
#                                print "'{}' is broader than '{}'".format(l, key) 
        
        return narrowers
        
        





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
        results = pickle.load(open(drugResultsFile,"r"))
    else :
        results = l.doQuery(l.aers_wrapper, q.aers_drug)
        pickle.dump(results, open(drugResultsFile,"w"))
    
    index = l.createIndex(results, {})
    narrowers = l.crossLink(index)
    
#    pprint(index)
#    pprint(narrowers)
    
    count = 0
    for key in narrowers:
        for k in index[key]:
            for n in narrowers[key] :    
                count += 1
                print "{}\t->\t{} ({})".format(n["nuri"],k["nuri"],k["label"])
    
    print "Results", len(results["results"]["bindings"])
    print "Index", len(index)
    print "Number of narrower relations", count
    
    
    