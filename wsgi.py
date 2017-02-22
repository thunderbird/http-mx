version = "0.04"

import DNS
DNS.DiscoverNameServers()

DEFAULT_TTL = 300
timeout = 10

def application(environ, start_response):
    data =  []
    domain = environ['PATH_INFO'].lstrip('/')
    status = "200 OK"
    ttl = DEFAULT_TTL

    if domain == '':
        data = "Thunderbird MX Lookup v%s running on %s\n" % (version, environ['SERVER_SOFTWARE'])
    else:
        error, mxes, ttl = mxlookup(domain)
        if not error and mxes:
            for mx in mxes:
                answer = "%s\n" % mx
                data.append(answer)
        elif error == 504:
            status = "504 Gateway Timeout"
            data = "DNS Server Timeout"
        else:
            status = "404 Not Found"
            data = "No MX data for %s\n" % domain

    expires = get_expires(ttl)
    length = sum([len(i) for i in data])

    start_response(status, [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(length)),
        ("X-Powered-By", "DNS-MX/%s" % version),
        ("Cache-Control", "public, max-age=%d" % ttl),
        ("Expires", expires)
    ])

    return data


def mxlookup(domain):
    try:
        result = DNS.DnsRequest(name=domain, qtype='mx', timeout=timeout).req()
    except DNS.Base.TimeoutError:
        return (504, False, False)

    answers = []
    ttls = []
    ttl = False
    error = 404
    if result.header['status'] == 'NOERROR' and result.answers:
        error = False
        for a in result.answers:
            answers.append(a['data'])
            ttls.append(a['ttl'])
        ttl = min(ttls)
        answers.sort()
        answers = map(lambda x: x[1], answers)

    return (error, answers, ttl)

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


