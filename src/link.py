from SPARQLWrapper import SPARQLWrapper, JSON, XML
from time import time
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, plugin, query
from d2s.prov import Trace

plugin.register('sparql', query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')


# Eculture
FULL_SPARQL_ENDPOINT = "http://eculture2.cs.vu.nl:5020/sparql/"
# Local
LOCAL_SPARQL_ENDPOINT = "http://localhost:8000/sparql/"

# Local
AERS_SPARQL_ENDPOINT = FULL_SPARQL_ENDPOINT
#"http://localhost:8080/openrdf-sesame/repositories/hubble"


wrapper = SPARQLWrapper(AERS_SPARQL_ENDPOINT)
wrapper.setReturnFormat(JSON)
wrapper.addCustomParameter('soft-limit','-1')



lld_wrapper = SPARQLWrapper("http://linkedlifedata.com/sparql")
lld_wrapper.setReturnFormat(JSON)

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

AERS = Namespace("http://aers.data2semantics.org/resource/")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
SIDER = Namespace("http://www4.wiwiss.fu-berlin.de/sider/resource/sider/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")



def slashURIToLabel(uri,regex):
    try :
        m = re.search(regex + r'(.*)$', uri)
        label = m.group(1)
        return label.replace('_',' ') 
    except :
        return uri

def doQuery(sparql, query, index, name='', labelFunction=None, regex=None):
    sparql.setQuery(query)
    print "Starting query {0}...".format(name)
#    print query
    
    tstart = time()
    res = sparql.query().convert()
    tend = time()
    print "... done ({0}us)".format(tend-tstart)
    resultsno = len(res["results"]["bindings"])
    print "Query returned {0} results.".format(resultsno)

    # Create Index
    for result in res["results"]["bindings"]:
        value = result["resource"]["value"]
        if labelFunction == None :
            key = result["label"]["value"].strip().lower()
        else :
            if regex == None :
                exec 'key ='+labelFunction+'("'+result["label"]["value"]+'").strip().lower()'
            else :
                exec 'key ='+labelFunction+'("'+result["label"]["value"]+'","'+regex+'").strip().lower()'
        index.setdefault(key, []).append((value,key))
    
    return index
    
def getMatches(index):
    # Retrieve all 'real' matches from the index 
    # (i.e. more than one resource per label, no duplicate resources per label)
    matches = []
    mcount = 0
    for (k,tuples) in index.iteritems() :
        if len(tuples) > 1 :
            sameAs = set()
            for (uri,label) in tuples :
                sameAs.add(uri)
                mcount = mcount + 1
            if len(sameAs) > 1 :   
                # print k, sameAs
                matches.append(sameAs)
            else :
                mcount = mcount - 1

    print "Found {0} matches on {1} labels!".format(mcount,len(matches))
    return matches    
    
def addMatchesToGraph(matches):
    g = ConjunctiveGraph()
    g.bind("aers", "http://aers.data2semantics.org/resource/")
    g.bind("dbpedia", "http://dbpedia.org/resource/")
    g.bind("owl", "http://www.w3.org/2002/07/owl#")
    g.bind("sider", "http://www4.wiwiss.fu-berlin.de/sider/resource/sider/")
    g.bind("skos","http://www.w3.org/2004/02/skos/core#")
    print "Adding to graph..."
    for m in matches :
        for subj in m :
            for obj in m :
                if subj != obj :
                    g.add((URIRef(subj),SKOS['exactMatch'],URIRef(obj)))
    print "... done"
    return g
    

                           
    
    

# Intialise indexes
drug_index = {}
diagnosis_index = {}
country_index = {}


# Initialise queries
aers_drug = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        ?resource   rdf:type    aers-vocab:Drug .
        ?resource   rdfs:label  ?label .
    } 
"""

aers_country = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        ?resource   rdf:type    aers-vocab:Country .
        ?resource   rdfs:label  ?label .
    } 
"""


aers_diagnosis = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    aers-vocab:Diagnosis . 
            ?resource   rdfs:label  ?label .
        }
        UNION
        {   ?resource   rdf:type    aers-vocab:Reaction . 
            ?resource   rdfs:label  ?label .
        }
    } 
"""

ctcae = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        ?resource   rdf:type    owl:Class .
        ?resource   rdfs:label  ?label .
    }
"""


dbpedia_drug = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    dbpedia-owl:Drug .
            ?resource   rdfs:label  ?label .
        } 
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:Drug .
            ?label      dbpedia-owl:wikiPageRedirects ?resource .
        }
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:ChemicalCompound .
            ?resource   rdfs:label  ?label .
        } 
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:ChemicalCompound .
            ?label      dbpedia-owl:wikiPageRedirects ?resource .
        } 
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:ChemicalSubstance .
            ?resource   rdfs:label  ?label .
        } 
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:ChemicalSubstance .
            ?label      dbpedia-owl:wikiPageRedirects ?resource .
        }
    } 
"""

dbpedia_country = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    dbpedia-owl:Country .
            ?resource   rdfs:label  ?label .
        } 
        UNION
        {
            ?resource   rdf:type    dbpedia-owl:Country .
            ?label      dbpedia-owl:wikiPageRedirects ?resource .
        }
    } 
"""

sider_drug = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    sider:drugs .
            ?resource   rdfs:label  ?label .
        }
        UNION
        {
            ?resource   rdf:type        sider:drugs .
            ?resource   sider:drugName  ?label .
        }    
        FILTER(?resource != <http://www4.wiwiss.fu-berlin.de/sider/resource/drugs/2232>)
    }
"""

sider_effect = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    sider:side_effects .
            ?resource   rdfs:label  ?label .
        }
        UNION
        {
            ?resource   rdf:type              sider:side_effects .
            ?resource   sider:sideEffectName  ?label .
        }    
    }
"""

linkedct_condition = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        ?resource   rdf:type            ct:condition .
        ?resource   ct:condition_name   ?label .
    }
"""

umls_drug = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        { 
            ?resource   calbc:hasCorrelation       calbc-group:CHEM .
            ?resource   skos-xl:prefLabel   ?prefLabel .
            ?prefLabel  skos-xl:literalForm ?label . 
        }
        UNION
        { 
            ?resource   calbc:hasCorrelation       calbc-group:CHEM .
            ?resource   skos-xl:altLabel   ?altLabel .
            ?altLabel   skos-xl:literalForm ?label .        
        }
    }"""
    
umls_diagnosis = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        { 
            ?resource   calbc:hasCorrelation       calbc-group:DISO .
            ?resource   skos-xl:prefLabel   ?prefLabel .
            ?prefLabel  skos-xl:literalForm ?label . 
        }
        UNION
        { 
            ?resource   calbc:hasCorrelation       calbc-group:DISO .
            ?resource   skos-xl:altLabel   ?altLabel .
            ?altLabel   skos-xl:literalForm ?label .        
        }
    }
"""

drugbank_drug = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        ?resource   rdf:type    drugbank:drugs .
        {
            ?resource   drugbank:brandName  ?label .
        }
        UNION
        {
            ?resource   drugbank:synonym  ?label .
        }
        UNION
        {
            ?resource   rdfs:label  ?label .
        }        
    }
"""

drug_index = doQuery(wrapper, aers_drug, drug_index, 'AERS Drug Names')

drug_index = doQuery(wrapper, ctcae, drug_index, 'CTCAE Drug Names')

drug_index = doQuery(wrapper, dbpedia_drug, drug_index, 'DBPedia Drug Names', 'slashURIToLabel', regex='http://dbpedia.org/resource/')

drug_index = doQuery(wrapper, sider_drug, drug_index, 'Sider Drug Names')

drug_index = doQuery(wrapper, drugbank_drug, drug_index, 'Drugbank Drug Names')

drug_index = doQuery(lld_wrapper, umls_drug, drug_index, 'UMLS Drug Names')

drug_matches = getMatches(drug_index)
    
drug_graph = addMatchesToGraph(drug_matches)    

drug_links_file = open('drug_links.nt','w')

print "Serializing to {0}...".format('drug_links.nt')
drug_graph.serialize(drug_links_file, format = 'nt')
print "... done"

diagnosis_index = doQuery(wrapper, aers_diagnosis, diagnosis_index, 'AERS diagnosis')

diagnosis_index = doQuery(wrapper, sider_effect, diagnosis_index, 'Sider Effects')

diagnosis_index = doQuery(wrapper, ctcae, diagnosis_index, 'CTCAE diagnosis Names')

diagnosis_index = doQuery(lld_wrapper, linkedct_condition, diagnosis_index, 'LinkedCT Conditions')

diagnosis_index = doQuery(lld_wrapper, umls_diagnosis, diagnosis_index, 'UMLS diagnosis')

diagnosis_matches = getMatches(diagnosis_index)

diagnosis_graph = addMatchesToGraph(diagnosis_matches)

diagnosis_links_file = open('diagnosis_links.nt','w')

print "Serializing to {0}...".format('diagnosis_links.nt')
diagnosis_graph.serialize(diagnosis_links_file, format = 'nt')
print "... done"

country_index = doQuery(wrapper, aers_country, country_index, 'AERS Country Names')

country_index = doQuery(wrapper, dbpedia_country, country_index, 'DBPedia Country Names', labelFunction='slashURIToLabel', regex='http://dbpedia.org/resource/')

country_matches = getMatches(country_index)
    
country_graph = addMatchesToGraph(country_matches)    

country_links_file = open('country_links.nt','w')

print "Serializing to {0}...".format('country_links.nt')
country_graph.serialize(country_links_file, format = 'nt')
print "... done"


