'''
Created on Jul 13, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from subprocess import check_output
import argparse
import re
import logging

## GLOBAL SETTINGS

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

logHandler = logging.StreamHandler()
logHandler.setLevel(logging.DEBUG)

logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logHandler.setFormatter(logFormatter)

log.addHandler(logHandler)




SPARQL_BASE = "http://eculture2.cs.vu.nl:5020"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", help="Skip interactive mode, just list the commands", action="store_true")
#    parser.add_argument("--curl", help="Use curl to upload the triples, instead of using 4s-import", action="store_true")
#    parser.add_argument("--prov-trail", help="Location of the provenance trail file, if it has not already been loaded to the 4store instance")
    args = parser.parse_args()
    
    sw = SPARQLWrapper('{}/sparql/'.format(SPARQL_BASE))
    query = """PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX dc:   <http://purl.org/dc/elements/1.1/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX frbr: <http://purl.org/vocab/frbr/core#> 

SELECT ?g ?f
WHERE {
    ?g prov:wasGeneratedBy ?activity .
    ?activity prov:hadPlan <http://aers.data2semantics.org/vocab/provenance/4s-import> .
    ?activity prov:used ?dump .
    ?dump frbr:realizationOf ?f
} ORDER BY ?g
"""
    
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    
    results = sw.query().convert()

    for res in results["results"]["bindings"] :
        g = res["g"]["value"]
        f = res["f"]["value"]
        
        fileName = re.search(".*/(.*?)\.nt", f).group(1) + ".nt"
        
        log.info("Graph: <{}>\nFile: {}".format(g, fileName))
        if args.list :
            log.info("4s-import aers -v --model {} {}".format(g,fileName))
        else :
            yn = raw_input("Upload this graph? (y/n/q): ")
            
            if yn == "y" :
                log.info("Importing into graph <{}>".format(g))
                log.info("Using 4s-import to load data locally")
                command = ["4s-import", "aersld","-v", "--model", g, fileName]
                out = check_output(command)
                log.debug(out)
                log.debug("Done")
            elif yn == "q":
                quit()
            else :
                log.info("Skipping...")
    
    log.info("Finished!")