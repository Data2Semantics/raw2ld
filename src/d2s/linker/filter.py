'''
Created on Jul 26, 2012

@author: hoekstra
'''
import argparse 
import re
from csv import reader, writer
import pickle


# Example Command Line
## Strict Diagnoses
## ../../../aers_research/all_ae_vs_drug.tsv (5-FU|CAPECITABINE) /(FEBRILE_NEUTROPENIA|NEUTROPENIA|LEUCOPENIA|VOMITING|THROMBOCYTOPENIA|DIARRHEA|DIARRHOEA|NAUSEA|STOMATITIS|HFS)^ --header --replacement other --regexin ^<http://aers.data2semantics.org/resource/(drug|diagnosis)/(.*)>$ --regexout \2  --output ../../../../aers_research/katoyama.tsv --urimap reverse_uri_index.pickle --narrowermap aers_drugs_broaders.pickle --test
## Relaxed
## ../../../../aers_research/all_ae_vs_drug.tsv (5-FU|CAPECITABINE) /(FEBRILE_NEUTROPENIA|NEUTROPENIA|LEUCOPENIA|VOMITING|THROMBOCYTOPENIA|DIARRHEA|DIARRHOEA|NAUSEA|STOMATITIS|HFS)^ --header --replacement other --regexin ^<http://aers.data2semantics.org/resource/(drug|diagnosis)/(.*)>$ --regexout \2  --output ../../../../aers_research/katoyama.tsv --urimap reverse_uri_index.pickle --narrowermap aers_drugs_broaders.pickle --test
## Strict Drugs
## ../../../../aers_research/all_ae_vs_drug.tsv /(5-FU|CAPECITABINE)> (FEBRILE_NEUTROPENIA|NEUTROPENIA|LEUCOPENIA|VOMITING|THROMBOCYTOPENIA|DIARRHEA|DIARRHOEA|NAUSEA|STOMATITIS|HFS) --header --replacement other --regexin ^<http://aers.data2semantics.org/resource/(drug|diagnosis)/(.*)>$ --regexout \2  --output ../../../../aers_research/katoyama_strict_drugs.tsv --urimap reverse_uri_index.pickle --narrowermap aers_drugs_broaders.pickle --test

def matchNarrower(i,regex):
    try :
        nuri = reverse_uri_index[row[i].strip('<>')]
        candidates = [nuri]
        
        if nuri in narrower_index:
            candidates.extend(narrower_index[nuri])
        
        for candidate in candidates :
            if re.search(regex,candidate,re.IGNORECASE) != None :
                if args.regexin and args.regexout :
                    nrow[i] = re.sub(args.regexin,args.regexout,nuri)
                else :
                    nrow[i] = nuri
            else :
                nrow[i] = replace
    except Exception as e:
        if re.search(left,row[i],re.IGNORECASE) != None :
            if args.regexin and args.regexout :
                nrow[i] = re.sub(args.regexin,args.regexout,row[i])
            else :
                nrow[i] = row[i]
        else :
            nrow[i] = replace

def match(i,regex):
    if re.search(regex,row[i],re.IGNORECASE) == None :
        nrow[i] = replace
    elif args.regexin and args.regexout :
        nrow[i] = re.sub(args.regexin,args.regexout,row[i])
    else :
        nrow[i] = row[i]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Filter a two-column TSV file")
    parser.add_argument('input', type=str, help="The input file name, must be tab separated (TSV)")
    parser.add_argument('left', type=str, help="The regex matching the string to keep in the left hand column")
    parser.add_argument('right', type=str, help="The regex matching the string to keep in the right hand column")
    parser.add_argument('--header', action='store_true', help="Use if the TSV file has a header row")
    parser.add_argument('--replacement', help="The replacement string for values that do not match left or right")
    parser.add_argument('--regexin', help="A regular expressing that can be used to rewrite matching values to something more readable")
    parser.add_argument('--regexout', help="The regular expression used to reformat the groups in --regexin")
    parser.add_argument('--output', help="The output file (if omitted, we will print to stdout)")
    parser.add_argument('--test', action='store_true', help="Only run on the first 100 rows")
    parser.add_argument('--urimap', help="Use URI mapping pickle (only used with --broadermap)")
    parser.add_argument('--narrowermap', help="Use narrower mapping pickle (only used with --urimap)")
    
    args = parser.parse_args()
    
    inFile = open(args.input, 'r')
    left = args.left
    right = args.right
    
    if args.urimap and args.narrowermap:
        print "Loading URI map from pickle"
        reverse_uri_index = pickle.load(open(args.urimap,"r"))
        print "Loading Broader map from pickle"
        narrower_index = pickle.load(open(args.narrowermap,"r"))
        
#        for k in reverse_uri_index:
#            print k, reverse_uri_index[k]
#        
#        for k in narrower_index :
#            print k, narrower_index[k]
    
    
    if args.replacement :
        replace = args.replacement
    else :
        replace = 'other'
    
    maxIterations = None
    if args.test :
        print "Just testing..."
        maxIterations = 1000
        
    
    r = reader(inFile, delimiter='\t')

    if args.header :
        print "Using header information"
        hrow = r.next()
    else:
        print "No header"
        hrow = None
        
    if args.output:
        print "Output to will be written to {}".format(args.output)
        outFile = open(args.output, 'w')
        w = writer(outFile, delimiter='\t')
        if hrow :
            w.writerow(hrow)
    else :
        print "Output will be written to screen"        
        
    count = 0
        
    for row in r :
        if len(row) > 2 and count == 0:
            print "Length of rows exceeds 2 columns: will only replace the first two columns!"
            
        count += 1
        nrow = row

        if args.urimap and args.narrowermap :
            matchNarrower(0,left)
            match(1,right)
        else :
            match(0,left)
            match(1,right)
            
            
        if args.output :
            w.writerow(nrow)
            if args.test :
                print "\t".join(nrow)
        else :
            print "\t".join(nrow)
        
        if count == maxIterations :
            break
    
    print "Wrote {} rows".format(count)
        
    
    
    
    
    