#!/usr/bin/env python

"""
./get.py http://localhost:8080/site/morethanseven
"""

import sys
import re
import socket

from django.utils import simplejson

from restful_lib import Connection

# check to see if we have the correct number of arguments
if len(sys.argv) != 2:
    print "You must provide a URL"
    sys.exit(1)
    
url_re = re.compile(
    r'^https?://' # http:// or https://
    r'(?:(?:[A-Z0-9-]+\.)+[A-Z]{2,6}|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|/\S+)$', re.IGNORECASE)

# check we have a valid url
if not url_re.match(sys.argv[1]):
    print "You must provide a valid URL"
    sys.exit(1)

# print a message as it may take time for the responce to return
print "Connecting to %s" % sys.argv[1]

# make the request
try:
    conn = Connection(sys.argv[1])
    # otherwise we should just print the response
    response = conn.request_get("/")
except socket.error:
    print "We couldn't connect to %s" % sys.argv[1]
    sys.exit(1)

if response['headers'].status == 200:
    print response['body']
else:
    print "Response was %s" % response['headers'].status
