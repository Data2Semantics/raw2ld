'''
Created on May 23, 2012

@author: hoekstra
'''

from rdflib import ConjunctiveGraph, URIRef, OWL
from SPARQLWrapper import SPARQLWrapper, JSON
import re

sparql = SPARQLWrapper('http://eculture2.cs.vu.nl:5020/sparql/')
sparql.setReturnFormat(JSON)

prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX aers-vocab: <http://aers.data2semantics.org/vocab/>
    PREFIX aers: <http://aers.data2semantics.org/resource/>
    PREFIX sider: <http://www4.wiwiss.fu-berlin.de/sider/resource/sider/>
    PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ct: <http://data.linkedct.org/resource/linkedct/>
    PREFIX calbc: <http://linkedlifedata.com/resource/calbc/>
    PREFIX calbc-group: <http://linkedlifedata.com/resource/calbc/group/>
    PREFIX drugbank: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/>
    PREFIX ctcae: <http://ncicb.nci.nih.gov/xml/owl/EVS/ctcae.owl#>
    
"""



cg = ConjunctiveGraph()
cg.load('../vocab/patient_example.n3', format="n3")

newcg = ConjunctiveGraph()


for s,p,o in cg.triples((None, None, None)) :
    m = re.search(r'http://linkedlifedata.com/.*',unicode(o))
    if m:
        q = prefixes + """
    SELECT ?uri WHERE {
        { ?uri owl:sameAs <"""+unicode(o)+"""> }
        UNION 
        { <"""+unicode(o)+"""> owl:sameAs ?uri }
    }
"""
        
        sparql.setQuery(q)
        results = sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            uri =  result["uri"]["value"]
            m2 = re.search(r"http://aers.data2semantics.org/.*",uri)
            if m2 :
                newcg.add((s,p,URIRef(uri)))
    else :
        if o != OWL["NamedIndividual"]:
            newcg.add((s,p,o))
        
out = open('../vocab/patient_example_new.n3','w')

newcg.serialize(out,format='n3')
                 
            
