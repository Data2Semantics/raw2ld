from BaseHTTPServer import BaseHTTPRequestHandler
import httplib
import urlparse
import xml.parsers.expat
import re

class GetHandler(BaseHTTPRequestHandler):
    
    # from http://boodebr.org/main/python/all-about-python-and-unicode#UNI_XML
    RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \
                     u'|' + \
                     u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                      (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                       unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
                       unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff))
    
    def do_GET(self):
        print "Request received"
        conn = httplib.HTTPConnection("eculture2.cs.vu.nl:5020")
        conn.request("GET", self.path)
        r1 = conn.getresponse()

        headers = r1.getheaders()
        headers.append(('Access-Control-Allow-Origin','*'))

        self.send_response(r1.status)
        for (key,value) in headers :
                self.send_header(key,value)
        self.end_headers()
        
        result = self.encode_characters(r1.read())
        
        self.wfile.write(result)
        print "Response sent"
        return


    def encode_characters(self, result):
        if result.startswith('<?xml') :
            print "xml!"
            p = xml.parsers.expat.ParserCreate()
            try :
                p.Parse(result)
                return result
            except :
                return re.sub(self.RE_XML_ILLEGAL, "?", result)
        else :
            return result


if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('', 5021), GetHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    (ip,port) = server.server_address
    print 'Server address: {0}:{1}'.format(ip,port)
    server.serve_forever()

