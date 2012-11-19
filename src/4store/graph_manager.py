'''
Created on Jul 6, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from subprocess import check_output
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("endpoint", nargs='?', help="The URL of the sparql endpoint (without /sparql suffix)", default='http://eculture2.cs.vu.nl:5020')
    args = parser.parse_args()
    
    SPARQL_BASE = args.endpoint
    
    sw = SPARQLWrapper('{}/sparql/'.format(SPARQL_BASE))
    query = "SELECT DISTINCT ?g WHERE { GRAPH ?g {?s ?p ?o}}"
    
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    
    results = sw.query().convert()
    
    for res in results["results"]["bindings"] :
        g = res["g"]["value"]
        print "Graph: <{}>".format(g)
        
        yn = raw_input("Delete this graph? (y/n/q): ")
        
        if yn == "y" :
            command = ["curl", "-X", "DELETE", "{}/data/{}".format(SPARQL_BASE,g)]
            print "Deleting graph <{}>".format(g)
            out = check_output(command)
            print out
            print "Done"
        elif yn == "q":
            quit()
        else :
            print "Skipping..."
    
    print "Finished!"
            
        