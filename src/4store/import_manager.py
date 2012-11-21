'''
Created on Jul 13, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from subprocess import call
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





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", nargs='?', help="The URL of the sparql endpoint (without /sparql suffix)", default='http://ops.few.vu.nl:8080')
    parser.add_argument("kb", nargs='?', help="The name of the 4Store knowledge base (backend)", default="data2semantics")
    parser.add_argument("--list", help="Skip interactive mode, just list the commands", action="store_true")
    parser.add_argument("--quiet", help="Don't ask, jus do!", action="store_true")
    parser.add_argument("--format", help="RDF Format as understood by 4store", default="ntriples")
    parser.add_argument("--virtuoso", help="List virtuoso load commands", action="store_true")
    parser.add_argument("--basedir", help="Base dir for virtuoso loader, ignored otherwise", default="/home/hoekstra/aers/data/dumps/")
#    parser.add_argument("--curl", help="Use curl to upload the triples, instead of using 4s-import", action="store_true")
#    parser.add_argument("--prov-trail", help="Location of the provenance trail file, if it has not already been loaded to the 4store instance")
    args = parser.parse_args()
    
    SPARQL_BASE = args.endpoint
    KB = args.kb
    FORMAT = args.format
    BASE_DIR = args.basedir
    
    log.debug("Will use {} to retrieve provenance informaiton".format(SPARQL_BASE))
    log.debug("Will load files in {} format to the {} 4store knowledge base".format(FORMAT, KB))
    if args.quiet:
        log.debug("Running in quiet mode")
    if args.list:
        log.debug("Running in list mode, not actually doing anything")
    
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

    list = []
    for res in results["results"]["bindings"] :
        g = res["g"]["value"]
        f = res["f"]["value"]
        
        fileName = re.search(".*/(.*?)\.nt", f).group(1) + ".nt"
        
        log.info("Graph: <{}>\nFile: {}".format(g, fileName))
        if args.virtuoso :
            commandstring = "ld_dir('{}','{}','{}');".format(BASE_DIR,fileName,g)
            log.info(commandstring)
            list.append(commandstring)
        elif args.list :
            commandstring = "4s-import {} -v --format {} --model {} {}".format(KB,FORMAT,g,fileName)
            log.info(commandstring)
            list.append(commandstring)
        else :
            if args.quiet :
                yn = "y"
            else :
                yn = raw_input("Upload this graph? (y/n/q): ")
            
            if yn == "y" :
                log.info("Importing into graph <{}>".format(g))
                log.info("Using 4s-import to load data locally")
                command = ["4s-import", KB ,"-v", "--format", FORMAT, "--model", g, fileName]
                out = call(command)
                log.debug(out)
                log.debug("Done")
            elif yn == "q":
                quit()
            else :
                log.info("Skipping...")
    
    if args.list or args.virtuoso:
        for c in list:
            print c
    
    log.info("Finished!")