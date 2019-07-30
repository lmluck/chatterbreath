from google.appengine.ext import ndb

class UserProfile(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    preferences = ndb.TextProperty()
    description = ndb.TextProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)