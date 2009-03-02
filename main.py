import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch, DownloadError

from models import Site

class Pinger(webapp.RequestHandler):
    """
    Trigger for all site pings
    We may need to refactor this out a little to support more
    than a few sites but this will do for now    
    """
    def get(self):
        
        # stub data
        """
        site = Site(
            name = "Localhost",
            url = db.Link("http://localhost:8000"),            
        )
        site.put()
        """

        # get all the sites we're going to ping
        sites = Site.all()

        # loop over all of the current sites
        for site in sites:
            try:
                # first off a request
                response = fetch(url=site.url, allow_truncated=True)
                # log everything to the debug log
                logging.debug("Made request for %s and got %s" % (site.url, response.status_code))
                # then do special things based on the request response
                if response.status_code == '404':
                    logging.error("Page not found at %s" % site.url)
                elif response.status_code == '500':
                    logging.error("Error on %s" % site.url)
            except DownloadError, e:
                # we also want to watch out for if the site doesn't 
                # respond at all
                logging.critical("Error accessing %s: %s" % (site.url, e))            

        self.redirect("/")
        
class Index(webapp.RequestHandler):
    """
    Main view for the application.
    Protected to logged in users only.
    """
    def get(self):

        # we are enforcing loggins so we know we have a user
        user = users.get_current_user()
        # we need the logout url for the frontend
        logout = users.create_logout_url("/")


        # get all the sites we're going to ping
        sites = Site.all()          

        # add the logour url to our template context
        context = {
            "logout": logout,
            "sites": sites
        }

        # prepare the context for the template
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))

# wire up the views
application = webapp.WSGIApplication([
    ('/', Index),
    ('/ping', Pinger),
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()