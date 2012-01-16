from SPARQLWrapper import SPARQLWrapper, XML, JSON
from time import time, sleep
import re
from rdflib import ConjunctiveGraph, Namespace, URIRef, plugin, query


plugin.register('sparql', query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
plugin.register('sparql', query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

OUT_FILE = 'drug_links.nt'


aers_sqw = SPARQLWrapper("http://eculture2.cs.vu.nl:5021/sparql/")
aers_sqw.setReturnFormat(JSON)
aers_sqw.addCustomParameter('soft-limit','-1')

lld_sqw = SPARQLWrapper("http://linkedlifedata.com/sparql")
lld_sqw.setReturnFormat(JSON)

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
    print "Adding to graph..."
    for m in matches :
        for subj in m :
            for obj in m :
                if subj != obj :
                    g.add((URIRef(subj),OWL['sameAs'],URIRef(obj)))
    print "... done"
    return g
    

                           
    
    

# Intialise indexes
drug_index = {}
indication_index = {}
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


aers_indication = prefixes + """
    SELECT DISTINCT ?resource ?label WHERE {
        {
            ?resource   rdf:type    aers-vocab:Indication . 
            ?resource   rdfs:label  ?label .
        }
        UNION
        {   ?resource   rdf:type    aers-vocab:Reaction . 
            ?resource   rdfs:label  ?label .
        }
    } 
"""

ctcae_drug = prefixes + """
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
    
umls_indication = prefixes + """
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

drug_index = doQuery(aers_sqw, aers_drug, drug_index, 'AERS Drug Names')

drug_index = doQuery(aers_sqw, ctcae_drug, drug_index, 'CTCAE Drug Names')

drug_index = doQuery(aers_sqw, dbpedia_drug, drug_index, 'DBPedia Drug Names', 'slashURIToLabel', regex='http://dbpedia.org/resource/')

drug_index = doQuery(aers_sqw, sider_drug, drug_index, 'Sider Drug Names')

drug_index = doQuery(aers_sqw, drugbank_drug, drug_index, 'Drugbank Drug Names')

drug_index = doQuery(lld_sqw, umls_drug, drug_index, 'UMLS Drug Names')

drug_matches = getMatches(drug_index)
    
drug_graph = addMatchesToGraph(drug_matches)    


print "Serializing to {0}...".format(OUT_FILE)
drug_graph.serialize(OUT_FILE, format = 'nt')
print "... done"

indication_index = doQuery(aers_sqw, aers_indication, indication_index, 'AERS Indications')

indication_index = doQuery(aers_sqw, sider_effect, indication_index, 'Sider Effects')

indication_index = doQuery(lld_sqw, linkedct_condition, indication_index, 'LinkedCT Conditions')

indication_index = doQuery(lld_sqw, umls_indication, indication_index, 'UMLS Indications')

print indication_index['febrile neutropenia']

indication_matches = getMatches(indication_index)

indication_graph = addMatchesToGraph(indication_matches)

print "Serializing to {0}...".format('indication_links.nt')
indication_graph.serialize('indication_links.nt', format = 'nt')
print "... done"

country_index = doQuery(aers_sqw, aers_country, country_index, 'AERS Country Names')

country_index = doQuery(aers_sqw, dbpedia_country, country_index, 'DBPedia Country Names', labelFunction='slashURIToLabel', regex='http://dbpedia.org/resource/')

country_matches = getMatches(country_index)
    
country_graph = addMatchesToGraph(country_matches)    

print "Serializing to {0}...".format('country_links.nt')
country_graph.serialize('country_links.nt', format = 'nt')
print "... done"


