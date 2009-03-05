import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch, DownloadError

from django.utils import simplejson

from models import Site, Ping
from lib import ping_site

class Pinger(webapp.RequestHandler):
    """
    Trigger for all site pings
    Depending on how many sites you have this might take too
    long and hit the appengine timeout. In which case it's time 
    to use the individual site pings
    """
    def get(self):
        "Ping each site in turn and record the response"
        # get all the sites we're going to ping
        sites = Site.all()

        # loop over all of the current sites
        for site in sites:
            # ping each site
            ping_site(site)           

        self.redirect("/")
        
class SitePinger(webapp.RequestHandler):
    """
    Trigger for a single site ping
    """
    def get(self, name):

        # get the site we're going to ping        
        try:
            # retrieve the site based on its name value
            site = Site.gql("WHERE name=:1", name)[0]
        except IndexError:
            # if we don't find a site then throw a Not Found error
            return self.error(404)        

        # ping the site and store the response
        ping_site(site)           

        # back to the home page
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

class Sites(webapp.RequestHandler):
    "Represents the collection of sites in JSON"

    def get(self):
        "List all the sites in JSON"
        
        # get all the sites
        sites = Site.all()

        # repreare out dict
        sites_for_output = {}
    
        # loop over the sites
        for site in sites:
            # and store each one in the output variable
            site_for_output = {
                "url": site.url,
                "email": site.email,
            }
            sites_for_output[site.name] = site_for_output
    
        # create the JSON object we're going to return
        json = simplejson.dumps(sites_for_output, sort_keys=False)

        # serve the response with the correct content type
        #self.response.headers['Content-Type'] = 'application/json'
        # write the json to the response
        self.response.out.write(json)

class SiteResource(webapp.RequestHandler):
    """
    Represenation of an individual site
    Allows for basic crud functionality
    """
    
    def get(self, name):
        "Show the JSON representing the site"
        try:
            # retrieve the site based on its name value
            site = Site.gql("WHERE name=:1", name)[0]
        except IndexError:
            # if we don't find a site then throw a Not Found error
            return self.error(404)
                
        # creat the object to represent the JSON object
        site_for_output = {
            "name": site.name,
            "url": site.url,
            "email": site.email,
        }
        
        # create the JSON from our object
        json = simplejson.dumps(site_for_output, sort_keys=False, indent=4)

        # serve the response with the correct content type
        #self.response.headers['Content-Type'] = 'application/json'
        # write the json to the response
        self.response.out.write(json)        
            
    def put(self, name):
        "Updates or Creates are managed through put on the name"
        
        # get the json from the body of the request
        json = self.request.body
        # convert the JSON to a Python object 
        representation = simplejson.loads(json)
        # set the properties
        url = representation['url']
        email = representation['email']
        
        # we need to check whether this is an update
        try:
           site = Site.gql("WHERE name=:1", name)[0]
           site.url = url
           site.email = email
        except IndexError:
            # or a create
            site = Site(
                name = name,
                url = db.Link(url),            
                email = db.Email(email),
            )      
        # either way we need to save the new object      
        site.put()
                
    def delete(self, name):
        "Delete the named resource"
        # check the resource exists
        try:
            # if it does then delete it
            site = Site.gql("WHERE name=:1", name)[0]
            site.delete()
        except IndexError:
            # site didn't exist
            return self.error(404)
        except:
            # something else went wrong
            return self.error(500)

# wire up the views
application = webapp.WSGIApplication([
    ('/site/([A-Za-z0-9]+)/ping/?$', SitePinger),
    ('/site/([A-Za-z0-9]+)/?$', SiteResource),
    ('/site/?$', Sites),
    ('/', Index),
    ('/ping', Pinger),
], debug=True)

def main():
    "Run the application"
    run_wsgi_app(application)

if __name__ == '__main__':
    main()