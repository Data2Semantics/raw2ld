'''
Created on Jul 5, 2012

@author: hoekstra
'''
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.highlight import PinpointFragmenter

if __name__ == '__main__':

    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, chars=True))
    ix = create_in("../indexdir", schema)
    writer = ix.writer()
    
    writer.add_document(title=u"Guideline", path=u"/a",
                         content=u"""Fever during chemotherapy-induced neutropenia may be the only indication of a severe underlying infection, because signs and symptoms of inflammation typically are attenuated. Physicians must be keenly aware of the infection risks, diagnostic methods, and antimicrobial therapies required for management of febrile patients through the neutropenic period. Accordingly, algorithmic approaches to fever and neutropenia, infection prophylaxis, diagnosis, and treatment have been established during the past 40 years, guided and modified by clinical evidence and experience over time.

The Infectious Diseases Society of America Fever and Neutropenia Guideline aims to provide a rational summation of these evolving algorithms. Summarized below are the recommendations made in the 2010 guideline update. A detailed description of the methods, background, and evidence summaries that support each of the recommendations can be found in the full text of the guideline.""")

    writer.commit()
    

    
    
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(u"neutropenia")
         
        matcher = query.matcher(searcher)
    
        # See
        # packages.python.org/Whoosh/api/matching.html#whoosh.matching.Matcher
         
        # For each document matching the query...
        while matcher.is_active():
            print "Docnum:", matcher.id()
            print "Score:", matcher.score()
            
            # spans() is only meaningful for fields with position info
            # (i.e. TEXT or a custom field type)
            print "List of occurances:"
            for span in matcher.spans():
                print "  Start word #", span.start, "End word #", span.end
                # This prints "None" unless you used chars=True in the field
                print "  Start char #", span.startchar, "End char #", span.endchar
            
            # Move to the next match
            matcher.next()
         
         