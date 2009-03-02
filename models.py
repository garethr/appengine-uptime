from google.appengine.ext import db

class Site(db.Model):
    name = db.StringProperty(required=True)
    url = db.LinkProperty(required=True)
    email = db.EmailProperty()
    
class Ping(db.Model):
    site = 
    date = db.DateTimeProperty(auto_now_add=True)
    code = db.IntegerProperty(required=True)
    up = db.BooleanProperty(default=True)

