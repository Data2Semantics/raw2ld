'''
Created on Jul 26, 2012

@author: hoekstra
'''
import argparse 
import re
from csv import reader, writer
import pickle
import copy
import yaml 



def matchBroader(i, strings, urimap, broadermap, relatedmap, match, replace, test):
    # Lookup the normalized uri from the reverse uri index
    normalized_uri = urimap[row[i].strip('<>')]
#    print row[i], normalized_uri

    intersection = []
    if normalized_uri in strings :
        # Just use the normalized URI
        intersection = [normalized_uri]
    else :
        # Add it to the list of candidates
        candidates = [normalized_uri]
        
        if normalized_uri in broadermap: 
            # Get all broader URIs for the normalized uri 
            candidates.extend(broadermap[normalized_uri])
        
        if normalized_uri in relatedmap: 
            # Get all related URIs for the normalized uri
            candidates.extend(relatedmap[normalized_uri])
        
        # Check for each of these URIs whether they are to be kept, or to be replaced
        # The result is a list that (hopefully) contains the current URI, or one of its broader concepts
        # This means that we will "keep" any URI that is either the same or more specific than the concept specified in the strings array.
        intersection = [val for val in candidates if val in strings]

    if len(intersection) == 0 :
        nrow[i] = replacement
    else :
        match_uri = intersection[0]
        
        if match and replace :
            nrow[i] = re.sub(match,replace,match_uri)
        else :
            nrow[i] = match_uri
        
        if test:
            print row[i], nrow[i]
            


def matchSimple(i,strings, match, replace):
    current = row[i].strip('<>')
    
    if current not in strings :
        nrow[i] = replacement
    elif match and replace :
        nrow[i] = re.sub(match,replace,current)
    else :
        nrow[i] = current

def loadMaps(lr, config):
    if 'urimap' in config[lr] and 'broadermap' in config[lr] and 'relatedmap' in config[lr]:
        urimap = config[lr]['urimap']
        broadermap = config[lr]['broadermap']
        relatedmap = config[lr]['relatedmap']
        print "Loading {} URI map from {}".format(lr, urimap)
        reverse_uri_index = pickle.load(open(urimap,"r"))
        print "Loading {} Broader map from {}".format(lr,broadermap)
        broader_index = pickle.load(open(broadermap,"r"))
        print "Loading {} Related map from {}".format(lr,relatedmap)
        related_index = pickle.load(open(relatedmap,"r"))
        return reverse_uri_index, broader_index, related_index
    else :
        return None, None, None
    
def cleanStrings(prefix, strings, urimap):
    if prefix and urimap:
        clean = [urimap[prefix+value] for value in strings]
    elif prefix :
        clean = [prefix+value for value in strings]
    else :
        clean = strings
    return clean


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter a two-column TSV file")
    parser.add_argument('config', type=str, help="The YAML configuration file", default='filter.yaml')
    
    
    args = parser.parse_args()
    
    config = yaml.load(open(args.config, "r"))
    
    

    
    # URImaps
    
    left_urimap, left_broadermap, left_relatedmap = loadMaps("left", config)
    right_urimap, right_broadermap, right_relatedmap = loadMaps("right", config)
        

    left = cleanStrings(config['left']['prefix'], config['left']['strings'], left_urimap)
    right = cleanStrings(config['right']['prefix'], config['right']['strings'], right_urimap)
        
    
    if 'replacement' in config :
        replacement = config['replacement']
    else :
        replacement = 'other'
    
    maxIterations = None
    if 'maxIterations' in config :
        print "Just testing..."
        maxIterations = config['maxIterations']
        
    print "Input: ", config['input']
    inFile = open(config['input'], 'r') 
    r = reader(inFile, delimiter='\t')

    if 'header' in config and config['header'] == True :
        print "Using header information"
        hrow = r.next()
    else:
        print "No header"
        hrow = None
        
    if 'output' in config:
        print "Output to will be written to {}".format(config['output'])
        outFile = open(config['output'], 'w')
        w = writer(outFile, delimiter='\t')
        if hrow :
            w.writerow(hrow)
    else :
        print "Output will be written to screen"   
        
    count = 0
    
    
    p = re.compile( r"[\\][\\](\d)" )

    match = config['regex']['match']
    replace = p.sub(r"\\\1", config['regex']['replace'])

    crosstable = {}
    crosstable_rows = set()
    crosstable_cols = set()
    
    
    for row in r :
        if len(row) > 2 and count == 0:
            print "Length of rows exceeds 2 columns: will only replace the first two columns!"
            
        count += 1
        nrow = copy.deepcopy(row)

        if left_urimap:
            matchBroader(0,left, left_urimap, left_broadermap, left_relatedmap, match, replace, config['test'])
        else:
            matchSimple(0, left, match, replace)
        
        if right_urimap:
            matchBroader(1, right, right_urimap, right_broadermap, right_relatedmap, match, replace, config['test'])
        else :
            matchSimple(1, right, match, replace)
            
        crosstable.setdefault(nrow[0],{}).setdefault(nrow[1],0)
        crosstable[nrow[0]][nrow[1]] += 1
        
        crosstable_rows.add(nrow[0])
        crosstable_cols.add(nrow[1])
        
        if 'output' in config :
            w.writerow(nrow)
            if count % 500000 == 0:
                print '... {} rows'.format(count)
        else :
            print "\t".join(nrow)
    

        
        if count == maxIterations :
            break
    
    print "\nWrote {} rows".format(count)
    
    
    
    if 'crosstable' in config:
        print "Writing crosstable to {}".format(config['crosstable'])
        outFile = open(config['crosstable'], 'w')
        w = writer(outFile, delimiter='\t')
        
        header = ['']
        header.extend(crosstable_cols)
        w.writerow(header)
        
        for r in crosstable_rows:
            rrow = [r]
            for c in crosstable_cols :
                if c in crosstable[r]:
                    rrow.append(crosstable[r][c])
                else :
                    rrow.append(0)
            w.writerow(rrow)
            
        print "DONE!"
            
    else :
        print "Crosstable:"   
        print "\t",
        for c in crosstable_cols :
            print c,
        print "\n",
        for r in crosstable_rows:
            print r,
            for c in crosstable_cols :
                if c in crosstable[r] :
                    print "{}\t".format(crosstable[r][c]),
                else :
                    print "0\t",
            print "\n",
        
    
    
    
    
    