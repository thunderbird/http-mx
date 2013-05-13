version = "0.04"

import DNS
DNS.DiscoverNameServers()

DEFAULT_TTL = 300

def application(environ, start_response):
    data =  []
    domain = environ['PATH_INFO'].lstrip('/')
    status = "200 OK"
    length = 0
    ttl = DEFAULT_TTL

    if domain == '':
        data = "Thunderbird MX Lookup v%s running on %s\n" % (version, environ['SERVER_SOFTWARE'])
        length = len(data)

    else:
      mxes, ttl = mxlookup(domain)

      if mxes:
        for mx in mxes:
          answer = "%s\n" % mx
          data.append(answer)
          length += len(answer)
      else:
          status = "404 Not Found"
          data = "Not such domain %s" % domain
          length = len(data)

    expires = get_expires(ttl)

    start_response(status, [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(length)),
        ("X-Powered-By", "DNS-MX/%s" % version),
        ("Cache-Control", "public, max-age=%d" % ttl),
        ("Expires", expires)
    ])

    return data


def mxlookup(domain):
    result = DNS.DnsRequest(name=domain, qtype='mx').req()
    answers = []
    ttls = []
    if result.header['status'] == 'NOERROR':
        for a in result.answers:
            answers.append(a['data'])
            ttls.append(a['ttl'])        
        ttl = min(ttls)
        answers.sort()
        answers = map(lambda x: x[1], answers)
        return (answers, ttl)
    else:
        return (False, 0)

from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
def get_expires(ttl):
    now = datetime.now() + timedelta(0, ttl)
    stamp = mktime(now.timetuple())
    return format_date_time(stamp)

if __name__ == '__main__':
    # this runs when script is started directly from commandline
    try:
        # create a simple WSGI server and run the application
        from wsgiref import simple_server
        print "Running test application - point your browser at http://localhost:8000/ ..."
        httpd = simple_server.WSGIServer(('', 8000), simple_server.WSGIRequestHandler)
        httpd.set_app(application)
        httpd.serve_forever()
    except ImportError:
        # wsgiref not installed, just output html to stdout
        for content in application({}, lambda status, headers: None):
            print content


