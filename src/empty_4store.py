'''
Created on May 22, 2012

@author: hoekstra
'''

from SPARQLWrapper import SPARQLWrapper, JSON
import subprocess

sw = SPARQLWrapper('http://eculture2.cs.vu.nl:5020/sparql/')
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
    print "Deleting graph <{}>".format(graph)
    
    # Preventing accidents, uncomment to activate
    # call = ["/usr/bin/curl","-X", "DELETE", "http://eculture2.cs.vu.nl:5020/data/{}".format(graph)]
    # subprocess.call(call)

