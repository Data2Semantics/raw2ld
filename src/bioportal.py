import httplib
import json
from rdflib import ConjunctiveGraph, URIRef, RDFS, Literal
import re

# Requirements for BioPortal connection
headers = {"Accept": "application/json"}
connection = httplib.HTTPConnection("rest.bioontology.org")
apikey = "4598fcf2-613c-4a36-af4f-98faa1e24a56"
ontologies_query = "/bioportal/ontologies?apikey={}"
concept_query = "/bioportal/virtual/ontology/{}?conceptid={}&apikey={}"

# linkedlifedata.com base uri
lld_base = "http://linkedlifedata.com/resource/umls/id/{}"

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
    abbr = ontology["abbreviation"]
    id = ontology["ontologyId"]
    ontology_map[abbr] = id

print "... done"

print "Loading annotations from file"
# Load the annotations from file

# If LOAD_FROM_RDF is set, we will load a file containing Annotation Ontology annotations, and get all objects of the hasTopic relation
# Otherwise, we read the URIs from a simple text file (one URI per line)
LOAD_FROM_RDF = False
bioportal_uris = set()

if LOAD_FROM_RDF :
    cg = ConjunctiveGraph()
    cg.parse("../../data/output-all.rdf",format="n3")
    
    
    for s,p,o in cg.triples((None, URIRef("http://purl.org/ao/core#hasTopic"), None)) :
        bioportal_uris.add(unicode(o))
else :
    bioportal_uris_file = open("../../data/hastopics.txt","r")
    for line in bioportal_uris_file.readlines() :
        bioportal_uris.add(line.rstrip())


print "... done"

#TEST = "http://purl.bioontology.org/ontology/MDR/10015919"

# Keep a list of all URIs we've visited
visited = []
counter = 0

print "Searching for UMLS ids in useful terms"
for bioportal_uri in bioportal_uris :
    if bioportal_uri not in visited :
        counter = counter + 1
        visited.append(bioportal_uri)
    
        print "{}: Checking for potential match in URI: {}".format(counter, bioportal_uri)
        # Example URI: http://purl.bioontology.org/ontology/MDR/10015919
        # "MDR" is the abbreviation of the ontology
        # "100159191" is the concept id
        m = re.search(r'http://purl.bioontology.org/ontology/(.+)/(.+)$', bioportal_uri)
        
        if m :
            # If there's a match
            try :
                ontology_abbr = m.group(1)
                ontology_id = ontology_map[ontology_abbr]
                concept_id = m.group(2)
                
                # Get the description of the concept from BioPortal as a JSON string
                connection.request("GET", concept_query.format(ontology_id,concept_id,apikey), "", headers)
                
                response = connection.getresponse()
                
                data = json.load(response)
                
                try :
                    concept_label = data["success"]["data"][0]["classBean"]["label"]
                    links_cg.add((bioportal_uri,RDFS.label,Literal(concept_label)))
#                    print "Inspecting {} ({})".format(concept_label,bioportal_uri)
                    
                    
                    for rel in data["success"]["data"][0]["classBean"]["relations"][0]["entry"] :
                        try :
                            if rel["string"] == "UMLS_CUI" :
                                umls_id = rel["list"][0]["string"]
                                if type(umls_id) != list: 
                                    lld_uri = lld_base.format(umls_id)
                                    print bioportal_uri, "->", lld_uri
                                    links_cg.add((URIRef(bioportal_uri),URIRef('http://www.w3.org/2002/07/owl#sameAs'),URIRef(lld_uri)))
                                else :
                                    for id in umls_id :
                                        lld_uri = lld_base.format(id)
                                        print bioportal_uri, "->", lld_uri
                                        links_cg.add((bioportal_uri,URIRef('http://www.w3.org/2002/07/owl#sameAs'),URIRef(lld_uri)))
                                        
                                    
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
links_cg.serialize(f,format="nt")

print "... done!"
        
        
        