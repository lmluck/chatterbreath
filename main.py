import os
import socialdata
import webapp2
import datetime
 
from google.appengine.api import users 
from google.appengine.ext.webapp import template


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
    if get_user_email():
        values['logout_url'] = users.create_logout_url('/')
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

class ProfileSaveHandler (webapp2.RequestHandler):
    def post(self):
        email = get_user_email()
        if not email:
            self.redirect('/')
        else:
            error_text = ''
            name = self.request.get('name')
            preferences = self.request.get('preferences')

            if len(name) < 2:
                error_text += "Name should be at least 2 characters. \n"
            if len(name) > 20:
                error_text += "Name should be no more than 20 characters. \n"    
            if len(name.split()) > 1:
                error_text += "Name should not have whitespace. \n"  
            if len(preferences) > 4000:
                error_text += "Description should be less than 4000 characters. \n"
            for word in preferences.split():
                if len(word) > 50:
                    error_text += "Description contas words that are too damned long. \n"       
                    break

            values = get_template_parameters()
            values['name'] = name
            values['preferences'] = preferences
            if error_text:
                values['errormsg'] = error_text

            else:
                socialdata.save_profile(email, name, preferences)
                values['successmsg'] = 'Everything worked out fine'
            render_template(self, 'profile-edit.html', values) 

class ProfileEditHandler(webapp2.RequestHandler):
   def get(self):
       email =  get_user_email()
       profile = socialdata.get_user_profile(email) #if no email then this function returns null
       values = get_template_parameters()
       values['name'] = 'Unkown'
       values['preferences'] = 'Profile does not exist'
       if profile:
           values['name'] = profile.name
           values['preferences'] = profile.preferences
       render_template(self, 'profile-edit.html', values)


class UserViewHandler(webapp2.RequestHandler):
    def get(self):
        profiles = socialdata.get_recent_profiles()
        values = get_template_parameters()
        values['profiles'] = profiles
        render_template(self, 'profilebase.html', values)




# -----------------CHAT---------------------

messages = []
class ChatHandler(webapp2. RequestHandler):
    def get(self):
        values = {
            'messages': messages
        }
        render_template(self, 'chatpage.html', values)
    def post(self):
        values = {
            'messages': messages
        }
        render_template(self, 'chatpage.html', values)
 
class ChatDisplayHandler(webapp2. RequestHandler):
    def get(self):
        values = {
            'messages': messages
        }
        render_template(self, 'chat.html', values)
    def post(self):
        values = {
            'messages': messages
        }
        render_template(self, 'chat.html', values)      

class Message():
    def __init__(self,timestamp,text):
        self.timestamp = timestamp
        self.text = text
class SendHandler(webapp2.RequestHandler):
    def post(self):
        chat_message = self.request.get('chatmsg')
        if len(chat_message) > 4000:
            self.response.out.write("That message is too long")
        else:
           timestamp = datetime.datetime.now()
           message = Message(timestamp,chat_message)
           messages.append(message)
           while len(messages ) > 50:
              messages.pop(0)
        
           self.redirect('/chatpage')
class PrintMessagesHandler(webapp2.RequestHandler):
    def get(self):
        print messages

app = webapp2.WSGIApplication([
    # ('/profile-list', ProfileListHandler),
    # ('/p/(.*)', ProfileViewHandler),
    ('/profile-save', ProfileSaveHandler),
    ('/chatdisplay', ChatDisplayHandler),
    ('/chatpage', ChatHandler),
    ('/print',PrintMessagesHandler),
    ('/send',SendHandler),
    ('/profile-edit', ProfileEditHandler),
    ('/profile-user', UserViewHandler),
    ('.*', MainHandler) #this maps the root url to the Main Page Handler
])