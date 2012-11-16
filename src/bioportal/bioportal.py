import httplib
import json
from rdflib import ConjunctiveGraph, URIRef, RDFS, Literal
from SPARQLWrapper import SPARQLWrapper, JSON
import re

# Requirements for BioPortal connection
headers = {"Accept": "application/json"}
connection = httplib.HTTPConnection("rest.bioontology.org")
apikey = "4598fcf2-613c-4a36-af4f-98faa1e24a56"
ontologies_query = "/bioportal/ontologies?apikey={}"
concept_query = "/bioportal/virtual/ontology/{}?conceptid={}&apikey={}"

# linkedlifedata.com base uri
lld_base = "http://linkedlifedata.com/resource/umls/id/{}"


# endpoint to use
sparql_endpoint = "http://localhost:8000/openrdf-sesame/repositories/d2smodule2"

# ontology_map will store all known ontologies and their abbreviations
ontology_map = {}

# links_cg will store all sameAs links between linkedlifedata URIs and BioOntology URIs
links_cg = ConjunctiveGraph()


print "Retrieving all ontology information from BioPortal"
connection.request("GET", ontologies_query.format(apikey), "", headers)
response = connection.getresponse()
data = json.load(response)

# Retrieve all ontologies, their ids and abbreviations from BioPortal (we can actually only use those with a BioPortal PURL)
for ontology in data["success"]["data"][0]["list"][0]["ontologyBean"]:
    try :
        abbr = ontology["abbreviation"]
        id = ontology["ontologyId"]
        ontology_map[abbr] = id
    except KeyError :
        print "Ontology {} does not have an abbreviation, cannot use it for linking!".format(ontology["ontologyId"])

print "... done"

print "Loading annotations ..."
# Load the annotations from file

# If LOAD_FROM_RDF is set, we will load a file containing Open Annotation annotations, and get all objects of the hasTopic relation
# Otherwise, we read the URIs from a simple text file (one URI per line)
LOAD_FROM_RDF = False
LOAD_FROM_SPARQL = True
bioportal_uris = set()

if LOAD_FROM_RDF :

    
    cg = ConjunctiveGraph()
    cg.parse("/Users/hoekstra/projects/data2semantics/MockupEntityRecognizer/annotations-first-list.n3",format="n3")
    cg.parse("/Users/hoekstra/projects/data2semantics/MockupEntityRecognizer/annotations-second-list.n3",format="n3")
    
    for s,p,o in cg.triples((None, URIRef("http://www.w3.org/ns/openannotation/extension/hasSemanticTag"), None)) :
        uo = unicode(o)
        
        m = re.search(r'http://purl.bioontology.org/ontology/(.+)/(.+)$', uo)
        
        if not m:
            # Find abbreviations and concept ids for OBO ontologies converted to OWL
            m = re.search(r'http://purl.org/obo/owl/(.+)#(.+)$', uo)
        
        if m :
            bioportal_uris.add(uo)
        
    for s,p,o in cg.triples((None, URIRef("http://www.w3.org/2004/02/skos/core#exactMatch"), None)) :
        bioportal_uris.add(unicode(s))
        bioportal_uris.add(unicode(o))
elif LOAD_FROM_SPARQL :

    
    sw = SPARQLWrapper(sparql_endpoint)
    query = """
PREFIX oax:<http://www.w3.org/ns/openannotation/extension/>
PREFIX skos:<http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?tag WHERE {
   ?x oax:hasSemanticTag ?tag .
}"""
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    results = sw.query().convert()
    
    for res in results["results"]["bindings"] :
        tag = res["tag"]["value"]
        
        m = re.search(r'http://purl.bioontology.org/ontology/(.+)/(.+)$', tag)
        
        if not m:
            # Find abbreviations and concept ids for OBO ontologies converted to OWL
            m = re.search(r'http://purl.org/obo/owl/(.+)#(.+)$', tag)
            
        if m :
            bioportal_uris.add(tag)
            print tag
    
#        if "match" in res :
#            bioportal_uris.add(res["match"]["value"])
#            print res["match"]["value"]
else :
    bioportal_uris_file = open("../../data/hastopics.txt","r")
    for line in bioportal_uris_file.readlines() :
        bioportal_uris.add(line.rstrip())


print "... done"

# TESTING PURPOSES ONLY
#TEST = "http://purl.org/obo/owl/DOID#DOID_8584"
#bioportal_uris = [TEST]

# Keep a list of all URIs we've visited (actually, we don't need this as bioportal_uris is a set!)
visited = []
counter = 0
total = len(bioportal_uris)

print "Searching for UMLS ids from (BioPortal) PURL URIs"
for bioportal_uri in bioportal_uris :
    if bioportal_uri not in visited :
        counter = counter + 1
        visited.append(bioportal_uri)
        
        # Example URI: http://purl.bioontology.org/ontology/MDR/10015919
        # "MDR" is the abbreviation of the ontology
        # "100159191" is the concept id
        m = re.search(r'http://purl.bioontology.org/ontology/(.+)/(.+)$', bioportal_uri)
        
        if not m:
            # Find abbreviations and concept ids for OBO ontologies converted to OWL
            m = re.search(r'http://purl.org/obo/owl/(.+)#(.+)$', bioportal_uri)
        
        if m :
            # If there's a match
            print "{}/{}: {}".format(counter, total, bioportal_uri)
            try :
                ontology_abbr = m.group(1)
                ontology_id = ontology_map[ontology_abbr]
                concept_id = m.group(2)
                
                # Get the description of the concept from BioPortal as a JSON string
                connection.request("GET", concept_query.format(ontology_id,concept_id,apikey), "", headers)
                
                response = connection.getresponse()
                
                data = json.load(response)
                
#                print data
                
                try :
                    concept_label = data["success"]["data"][0]["classBean"]["label"]
                    links_cg.add((URIRef(bioportal_uri),RDFS.label,Literal(concept_label)))
#                    print "Inspecting {} ({})".format(concept_label,bioportal_uri)
#                    print "Label: {}".format(concept_label)
                    
                    for rel in data["success"]["data"][0]["classBean"]["relations"][0]["entry"] :
#                        print "Rel: {}".format(rel)
#                        print "String: {}".format(rel["string"])
                        try :
                            if rel["string"] == "UMLS_CUI" :
                                umls_id = rel["list"][0]["string"]
                                if type(umls_id) != list: 
                                    lld_uri = lld_base.format(umls_id)
                                    print "\t\t{}".format(lld_uri)
                                    links_cg.add((URIRef(bioportal_uri),URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),URIRef(lld_uri)))
                                else :
                                    for id in umls_id :
                                        lld_uri = lld_base.format(id)
                                        print "\t\t{}".format(lld_uri)
                                        links_cg.add((URIRef(bioportal_uri),URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),URIRef(lld_uri)))
                            elif rel["string"] == "xref_EXACT SYNONYM":
                                for entry in rel["list"]:
#                                    print "Entry: {}".format(entry)
                                    if type(entry) == dict :
                                        for e in entry["string"] :
#                                            print "E: {}".format(e)
                                            em = re.search(r'UMLS_CUI:(.+)', e)
                                            if em :
                                                lld_uri = lld_base.format(em.group(1))
                                                print "\t\t{}".format(lld_uri)
                                                links_cg.add((URIRef(bioportal_uri),URIRef('http://www.w3.org/2004/02/skos/core#exactMatch'),URIRef(lld_uri)))
                                        
                                    
                        except KeyError:
                            print "Could not find UMLS_CUI in data:\n {}".format(rel)
                        except Exception as e:
                            print "Something went wrong:", e
                except KeyError:
                    print "No success in retrieving data for ontology {} and concept {}...".format(ontology_id,concept_id)
            except :
                print "Ontology abbreviation {} not found in ontology map (no id found)".format(ontology_abbr)
    else: 
        print "Ontology {} already visited!".format(bioportal_uri)
            
print "... done!"

print "Serializing to file"
f = open('bioportal_links.nt','w')
links_cg.serialize(f, format="nt")

print "... done!"
        
        
        