'''
Created on Jul 6, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
from subprocess import check_output

SPARQL_BASE = "http://eculture2.cs.vu.nl:5020"

if __name__ == '__main__':
    sw = SPARQLWrapper('{}/sparql/'.format(SPARQL_BASE))
    query = "SELECT DISTINCT ?g WHERE { GRAPH ?g {?s ?p ?o}}"
    
    sw.setQuery(query)
    sw.setReturnFormat(JSON)
    
    results = sw.query().convert()
    
    for res in results["results"]["bindings"] :
        g = res["g"]["value"]
        print "Graph: <{}>".format(g)
        
        yn = raw_input("Delete this graph? (y/n): ")
        
        if yn == "y" :
            command = ["curl", "-X", "DELETE", "{}/data/{}".format(SPARQL_BASE,g)]
            print "Deleting graph <{}>".format(g)
            out = check_output(command)
            print out
            print "Done"
        else :
            print "Skipping..."
    
    print "Finished!"
            
        