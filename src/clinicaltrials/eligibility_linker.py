'''
Created on Jun 29, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, XML, JSON
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, OWL

ELIGIBLITY_ENDPOINT = "http://localhost:8080/openrdf-sesame/repositories/eligibility4"

LLD_PREFIX = "http://linkedlifedata.com/resource/umls/id/"

LCT_PREFIX = "http://data.linkedct.org/resource/trial/"

sw = SPARQLWrapper(ELIGIBLITY_ENDPOINT)


cg = ConjunctiveGraph()
cg.bind("elc", "http://aers.data2semantics.org/resource/criterion/")
cg.bind("lld", "http://linkedlifedata.com/resource/umls/id/")
cg.bind("lct", "http://data.linkedct.org/resource/trial/")
cg.bind("owl", "http://www.w3.org/2002/07/owl#")

query = """
PREFIX :<http://www.w3.org/2002/07/owl#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:<http://www.w3.org/2002/07/owl#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX lc:<http://aers.data2semantics.org/resource/criterion/>

SELECT ?concept ?umlsid WHERE {
    ?concept lc:hasConceptId ?umlsid
}
"""

sw.setQuery(query)
sw.setReturnFormat(JSON)
res = sw.query().convert()



for result in res["results"]["bindings"]:
    concept = result["concept"]["value"]
    umlsid = result["umlsid"]["value"]
    
    lld_uri = URIRef(LLD_PREFIX + umlsid)
    
    concept_uri = URIRef(concept)
    print concept_uri, "sameAs", lld_uri
    cg.add((concept_uri, OWL["sameAs"], lld_uri))



query = """
PREFIX :<http://www.w3.org/2002/07/owl#>
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:<http://www.w3.org/2002/07/owl#>
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX lc:<http://aers.data2semantics.org/resource/criterion/>

SELECT ?trial WHERE {
    ?trial lc:hasCriterion ?x .
}
"""

sw.setQuery(query)
sw.setReturnFormat(JSON)
res = sw.query().convert()



for result in res["results"]["bindings"]:
    trial = result["trial"]["value"]
    
    trialcode = trial.replace("http://aers.data2semantics.org/resource/criterion/Trial","")
    
    lct_uri = URIRef(LCT_PREFIX + trialcode)
    
    trial_uri = URIRef(trial)
    print trial_uri, "sameAs", lct_uri
    cg.add((trial_uri, OWL["sameAs"], lct_uri))
    

cg.serialize(open("eligibility_links.ttl","w"), format="turtle")
    