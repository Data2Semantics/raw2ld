'''
Created on Jul 6, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from subprocess import check_output
import argparse
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
    parser.add_argument("endpoint", nargs='?', help="The URL of the sparql endpoint (without /sparql suffix)", default='http://eculture2.cs.vu.nl:5020')
    parser.add_argument("--empty", help="Empty the 4Store model completely", action="store_true")
    args = parser.parse_args()
    
    SPARQL_BASE = args.endpoint
    log.info('Using {} as 4Store location.'.format(SPARQL_BASE))
    sw = SPARQLWrapper('{}/sparql/'.format(SPARQL_BASE))
    sw.setReturnFormat(JSON)
    sw.addCustomParameter('soft-limit','-1')
    
    if args.empty :
        yn = raw_input("Are you sure you want to delete all graphs from {} (y/n): ".format(SPARQL_BASE))
        
        if yn == "y" :
            sw.setReturnFormat(JSON)
            sw.addCustomParameter('soft-limit','-1')
            
            q = """SELECT DISTINCT ?g WHERE {
             GRAPH ?g {
               ?s ?p ?o .
             }
            } """
            
            
            sw.setQuery(q)
            
            results = sw.query().convert()
            
            for result in results["results"]["bindings"] :
                graph = result["g"]["value"]
                log.info("Deleting graph <{}>".format(graph))
        else :
            log.info("Quitting...")
    else :
        query = "SELECT DISTINCT ?g WHERE { GRAPH ?g {?s ?p ?o}}"
        
        sw.setQuery(query)
        sw.setReturnFormat(JSON)
        
        results = sw.query().convert()
        
        for res in results["results"]["bindings"] :
            g = res["g"]["value"]
            log.info("Graph: <{}>".format(g))
            
            yn = raw_input("Delete this graph? (y/n/q): ")
            
            if yn == "y" :
                command = ["curl", "-X", "DELETE", "{}/data/{}".format(SPARQL_BASE,g)]
                log.info("Deleting graph <{}>".format(g))
                out = check_output(command)
                print out
                log.debug("Done")
            elif yn == "q":
                quit()
            else :
                log.info("Skipping...")
        
        log.info("Finished!")
            
        