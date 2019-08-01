import os
import socialdata
import logging
import webapp2
import datetime
import neighborhoods
 
from google.appengine.api import images 
from google.appengine.api import users 
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext.webapp import template


PREFERENCES = [
    'Football', 
    'Basketball', 
    'Soccer', 
    'Baseball',
    'Fashion',
    'Movies',
    'Video Games',
    'Swimming',
]


def render_template(handler, file_name, template_values):
    path = os.path.join(os.path.dirname(__file__), 'templates/'+ file_name)
    handler.response.out.write(template.render(path, template_values))

def get_user_email():
    user = users.get_current_user()
    if user:
        return user.email()
    else:
        return None

def get_template_parameters():
    values = {}
    email = get_user_email()
    if get_user_email():
        values['logout_url'] = users.create_logout_url('/')
        values['upload_url'] = blobstore.create_upload_url('/profile-save')
        values['user'] = email
    else:
        values['login_url'] = users.create_login_url('/')
    return values


class MainHandler(webapp2.RequestHandler):
    def get(self):
        values = get_template_parameters()
        if get_user_email():
            profile = socialdata.get_user_profile(get_user_email())
            if profile:
                values['name'] = profile.name
        render_template(self, 'welcome.html', values)

class ProfileSaveHandler (blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        email = get_user_email()
        if not email:
            self.redirect('/')
        else:
            error_text = ''
            upload_files = self.get_uploads()
            blob_info = upload_files[0]
            type = blob_info.content_type
            name = self.request.get('name')
            preferences = self.request.get('preferences', allow_multiple=True)
            neighborhood = self. request.get('neighborhood')
            print 'Preferences: '
            print preferences
            print 'Neighborhood: '
            print neighborhood

            values = get_template_parameters()
            values['name'] = "Joe"
            if type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
                name= self.request.get('name')
                my_image= MyImage()
                my_image.name = name
                my_image.user = values['user']
                my_image.image = blob_info.key()
                my_image.put()
                image_id = my_image.key.urlsafe()
                socialdata.save_profile(email, name, preferences, neighborhood, blob_info.key())
                self.redirect('/image?id=' + image_id)

            if len(name) < 2:
                error_text += "Name should be at least 2 characters. \n"
            if len(name) > 20:
                error_text += "Name should be no more than 20 characters. \n"    
            if len(name.split()) > 1:
                error_text += "Name should not have whitespace. \n"  
            if error_text:
                values['errormsg'] = error_text

            else:
                socialdata.save_profile(email, name, preferences, neighborhood, blob_info.key())
                values['successmsg'] = 'Everything worked out fine'
            self.redirect('/profile-edit')

class ProfileEditHandler(webapp2.RequestHandler):
   def get(self):
       email =  get_user_email()
       profile = socialdata.get_user_profile(email) #if no email then this function returns null

       values = get_template_parameters()
       values['name'] = 'Unkown'
       values['preferences'] = PREFERENCES
       values['neighborhood_options'] = neighborhoods.neighborhoods
       if profile:
           values['name'] = profile.name
           values['userpreferences'] = profile.preferences
           values['neighborhood'] = profile.neighborhood
       render_template(self, 'profile-edit.html', values)


class UserViewHandler(webapp2.RequestHandler):
    def get(self):
        profiles = socialdata.get_recent_profiles()
        values = get_template_parameters()
        values['profiles'] = profiles
        render_template(self, 'profilebase.html', values)

class ChattiesListHandler(webapp2.RequestHandler):
    def get(self):
        profiles = socialdata.get_user_compatibilities(get_user_email())
        values = get_template_parameters()
        user = users.get_current_user()
        current_user = socialdata.get_user_profile(user.email())
        values['profiles'] = profiles
        values['name'] = current_user.name
        render_template(self, 'chatties_list.html', values)

class PreferencesHandler(webapp2.RequestHandler):
    def get(self):
        values = get_template_parameters()
        values['name'] = 'Unkown'
        values['preferences'] = 'Profile does not exist'
        render_template(self, 'preferences.html', values)
        
class MainPageHandler(webapp2.RequestHandler):
    def get(self):
        #make sure to get user profile so you can get the users name
        # values['user_name'] = profile.name + ('-')
        user = users.get_current_user()
        current_user = socialdata.get_user_profile(user.email())
        values = {}
        profiles = socialdata.get_user_compatibilities(get_user_email())
        display_pref = []
        all_lists = [person.preferences for person in profiles]
        for list in all_lists:
            display_pref.append([str(pref) for pref in list])
        values = get_template_parameters()
        name_list = [current_user.name +profile.name for profile in profiles]
        values['profiles'] = zip([profile.name for profile in profiles], display_pref, name_list)
        render_template(self, 'main.html', values)
# -----------------CHAT---------------------

messages = []

class ChatHandler(webapp2. RequestHandler):
    def get(self, namepair):
        list_names = namepair.split("-")
        print list_names
        values = {
            'messages': messages,
            'listnames': list_names,
            'namepair': namepair,
            'current_user': list_names[0],
            'matched_user': list_names[1]
        }
        render_template(self, 'chatpage.html', values)
    def post(self, namepair):
        list_names = namepair.split("-")
        values = {
            'messages': messages,
            'listnames': list_names,
            'namepair': namepair,
            'current_user': list_names[0],
            'matched_user': list_names[1]
        }
        render_template(self, 'chatpage.html', values)
 
class ChatDisplayHandler(webapp2. RequestHandler):
    def get(self, namepair): #says how name pair must be formatted, name1-name2
        list_names = namepair.split("-")
        print list_names[0]

        values = {
            'messages': messages,
            'listnames': list_names,
            'namepair': namepair,
            'current_user': list_names[0],
            'matched_user': list_names[1]
        }
        render_template(self, 'chat.html', values)
    def post(self):
        values = {
            'messages': messages
        }
        render_template(self, 'chat.html', values)      

class Message():
    def __init__(self,timestamp,text, sender, recipient):
        self.timestamp = timestamp
        self.text = text
        self.sender = sender
        self.recipient = recipient


class SendHandler(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        current_user = socialdata.get_user_profile(user.email())
        chat_message = self.request.get('chatmsg')
        matched_user = self.request.get('matched_user')
        namepair = current_user.name + '-' + matched_user
        print "Namepair: " + namepair
        if len(chat_message) > 4000:
            self.response.out.write("That message is too long")
        else:
           timestamp = datetime.datetime.now()
           message = Message(timestamp, chat_message, current_user.name, matched_user)
           messages.append(message)
           while len(messages ) > 50:
              messages.pop(0)
        
           self.redirect('/chatpage/' + namepair)

class PrintMessagesHandler(webapp2.RequestHandler):
    def get(self):
        print messages

class  MyImage(ndb.Model):
    name= ndb.StringProperty()
    image = ndb.BlobKeyProperty()
    user = ndb.StringProperty()

class ImageManipulationHandler(webapp2.RequestHandler):
      def get(self):
 
       image_id = self.request.get("id")
       my_image = ndb.Key(urlsafe=image_id).get()
       blob_key = my_image.image
       img = images.Image(blob_key=blob_key)
      
       print(img)
 
       modified = False
 
       h = self.request.get('height')
       w = self.request.get('width')
       fit = False
 
       if self.request.get('fit'):
           fit = True
 
       if h and w:
           img.resize(width=int(w), height=int(h), crop_to_fit=fit)
           modified = True
 
       optimize = self.request.get('opt')
       if optimize:
           img.im_feeling_lucky()
           modified = True
 
       flip = self.request.get('flip')
       if flip:
           img.vertical_flip()
           modified = True
 
       mirror = self.request.get('mirror')
       if mirror:
           img.horizontal_flip()
           modified = True
 
       rotate = self.request.get('rotate')
       if rotate:
           img.rotate(int(rotate))
           modified = True
 
       result = img
       if modified:
           result = img.execute_transforms(output_encoding=images.JPEG)
       print("about to render image")
       img.im_feeling_lucky()
       self.response.headers['Content-Type'] = 'image/png'
       self.response.out.write(img.execute_transforms(output_encoding=images.JPEG))


class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self):
        user_id = self.request.get('id')
        profile = ndb.Key(urlsafe=user_id).get()
        self.send_blob(profile.profile_pic)


app = webapp2.WSGIApplication([
    # ('/profile-list', ProfileListHandler),
    # ('/p/(.*)', ProfileViewHandler),
    ('/img', ImageManipulationHandler),
    ('/chatties-list', ChattiesListHandler),
    ('/profile-save', ProfileSaveHandler),
    ('/chatdisplay/(.*)', ChatDisplayHandler),#the i-frame for the chatpage
    ('/preferences', PreferencesHandler),
    ('/chatpage/(.*)', ChatHandler), #the user-interactive chat page
    ('/print',PrintMessagesHandler),
    ('/send',SendHandler),
    ('/mainpage', MainPageHandler),
    ('/profile-edit', ProfileEditHandler),
    ('/profile-user', UserViewHandler),
    ('/profilepic', ViewPhotoHandler),
    ('.*', MainHandler) #this maps the root url to the Main Page Handler
])