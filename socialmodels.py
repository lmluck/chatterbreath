from google.appengine.ext import ndb

class UserProfile(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    preferences = ndb.StringProperty(repeated=True)
    neighborhood = ndb.StringProperty()
    profile_pic=ndb.BlobKeyProperty()
    description = ndb.TextProperty()
    last_update = ndb.DateTimeProperty(auto_now=True)
