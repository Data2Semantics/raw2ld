'''
Created on Dec 7, 2012

@author: hoekstra
'''
from csv import reader
from glob import glob
import argparse
import os.path
import logging

TRANSLATION_TABLE = 'graph_mappings.csv'
GRAPH_BASE = 'http://aers.data2semantics.org/resource/graph/'

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
    
    parser.add_argument('path',help='Path to prepare')
    
    args = parser.parse_args()
    
    path = args.path
    if not path.endswith('/') :
        path += '/'
    
    files = []
    
    files.extend(glob("{}*.nt".format(path)))
    files.extend(glob("{}*.n3".format(path)))
    files.extend(glob("{}*.ttl".format(path)))
    files.extend(glob("{}*.owl".format(path)))
    
    r = reader(open(TRANSLATION_TABLE,"r"),delimiter=';')
    
    table = {}
    for row in r:
        table.setdefault(row[0], row[1])
    
    for p in files :
        (dir,f) = os.path.split(p)
        
        if f in table:
            graph_uri = table[f]
            log.info("Found graph URI <{}> for '{}'".format(graph_uri,f))
        else :
            graph_uri = "{}{}".format(GRAPH_BASE,f)
            log.info("Generated graph URI <{}> for '{}'".format(graph_uri,f))

        
        graph_filename = "{}.graph".format(p)
        
        # Open a file with the graph_filename name, if it already exists: overwrite
        graph_file = open(graph_filename,"w")
        
        graph_file.write("{}\n".format(graph_uri))
        log.info("Wrote <{}> to '{}'".format(graph_uri,graph_filename))
    
    