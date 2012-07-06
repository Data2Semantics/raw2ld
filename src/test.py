'''
Created on Jul 6, 2012

@author: hoekstra
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Namespace, ConjunctiveGraph, URIRef

# Eculture
FULL_SPARQL_ENDPOINT = "http://eculture2.cs.vu.nl:5020/sparql/"
# Local
LOCAL_SPARQL_ENDPOINT = "http://localhost:8000/sparql/"

# Local
AERS_SPARQL_ENDPOINT = FULL_SPARQL_ENDPOINT
#"http://localhost:8080/openrdf-sesame/repositories/hubble"

prefixes = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX dbpedia: <http://dbpedia.org/resource/>
    PREFIX aersv: <http://aers.data2semantics.org/vocab/>
    PREFIX aers: <http://aers.data2semantics.org/resource/>
    PREFIX sider: <http://www4.wiwiss.fu-berlin.de/sider/resource/sider/>
    PREFIX skos-xl: <http://www.w3.org/2008/05/skos-xl#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX ct: <http://data.linkedct.org/resource/linkedct/>
    PREFIX calbc: <http://linkedlifedata.com/resource/calbc/>
    PREFIX calbc-group: <http://linkedlifedata.com/resource/calbc/group/>
    PREFIX drugbank: <http://www4.wiwiss.fu-berlin.de/drugbank/resource/drugbank/>
    PREFIX ctcae: <http://ncicb.nci.nih.gov/xml/owl/EVS/ctcae.owl#>
    PREFIX d2sa: <http://aers.data2semantics.org/vocab/annotation/>
    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
    PREFIX oax:  <http://www.w3.org/ns/openannotation/extension/>
    PREFIX swanrel: <http://purl.org/swan/2.0/discourse-relationships/>
    
"""

AERS = Namespace("http://aers.data2semantics.org/resource/")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
SIDER = Namespace("http://www4.wiwiss.fu-berlin.de/sider/resource/sider/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")



#

#    ?taga oax:hasSemanticTag ?tag .
#    ?tag skos:relatedMatch ?aerstag .
#    ?patient rdf:type <http://www.data2semantics.org/ontology/patient/Patient> .

if __name__ == '__main__':
    wrapper = SPARQLWrapper(AERS_SPARQL_ENDPOINT)
    wrapper.setReturnFormat(JSON)
    wrapper.addCustomParameter('soft-limit','-1')
    
    q = """
SELECT DISTINCT ?r ?b ?aerstag ?tag ?p WHERE 
{ 
    <http://aers.data2semantics.org/resource/patient/john_doe> ?p ?aerstag .
    ?tag skos:relatedMatch ?aerstag .
    ?taga oax:hasSemanticTag ?tag .
    ?r rdf:type d2sa:RecommendationAnnotation . 
    ?r oa:hasBody ?b .
    ?r d2sa:hasEvidenceSummary ?es .
    ?es swanrel:referencesAsSupportingEvidence ?ev .
    ?ev oa:hasTarget ?tg .
    ?tg oa:hasSource ?s .
    ?s owl:sameAs ?doc .
    ?ta2 oa:hasSource ?doc .
    ?taga oa:hasTarget ?ta2 .
} LIMIT 300"""
        
    print "Querying for "+ q
    wrapper.setQuery(prefixes+q)
    results = wrapper.query().convert()
    
    print len(results["results"]["bindings"])
    for res in results["results"]["bindings"] :
        print res["r"]["value"], res["b"]["value"], res["aerstag"]["value"], res["tag"]["value"], res["p"]["value"]


    
    