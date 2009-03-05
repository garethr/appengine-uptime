import logging

from google.appengine.api.urlfetch import fetch, DownloadError

from models import Ping

def ping_site(site):
    """
    Utility function which, when passed a site object, sends 
    an HTTP GET request and logs the response
    """
    try:
        # first off make a request
        response = fetch(url=site.url, allow_truncated=True)
        # log everything to the debug log
        logging.debug("Made request for %s and got %s" % (site.url, response.status_code))
        # record the event
        ping = Ping(
            site = site,
            code = response.status_code,
        )
        # then do special things based on the request response
        if response.status_code == '404':
            logging.error("Page not found at %s" % site.url)
            ping.up = False
        elif response.status_code == '500':
            logging.error("Error on %s" % site.url)
            ping.up = False
        # save the event
        ping.put()
    except DownloadError, e:
        # we also want to watch out for if the site doesn't 
        # respond at all
        ping = Ping(
            site = site,
            code = 408, # 408 is request timeout
            up = False,
        )
        ping.put()
        logging.error("Error accessing %s: %s" % (site.url, e))