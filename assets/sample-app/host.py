
import cgi
import os

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# http://code.google.com/appengine/docs/python/images/usingimages.html
from google.appengine.api import images

CONST_SITE_SERVICE = "localhost:8080"
CONST_CSS_SERVICE = "www.telasocial.com"

class Contact(db.Model):
  name      = db.StringProperty()
  user      = db.UserProperty()
  shortname = db.StringProperty()
  theme_id  = db.StringProperty()
  content = db.StringProperty(multiline=True)
  date    = db.DateTimeProperty(auto_now_add=True)

class Image(db.Model):
  referenceKey  = db.StringProperty()
  title         = db.StringProperty()
  description   = db.StringProperty()
  graphic       = db.BlobProperty(default=None)

class Plain_Show(webapp.RequestHandler):
  def get(self):
      shortname = self.request.get('k')
      contacts_query = Contact.all()
      contacts_query.filter("shortname =", shortname )
      #contacts = contacts_query.fetch(1)
      contact  = contacts_query.get()

      userImages = []
      mainObjectKey = str(contact.key())
      images        = findImages(mainObjectKey)

      template_values = {
       'theme_id_base': 'http://'+CONST_CSS_SERVICE+'/'+contact.theme_id+'/style/base.css',
       'theme_id_tabs': 'http://'+CONST_CSS_SERVICE+'/'+contact.theme_id+'/style/tabs.css',
       'theme_id_button': 'http://'+CONST_CSS_SERVICE+'/'+contact.theme_id+'/style/button.css',
       'user_images': images,  # See above, the list of images if this user has 
       'contact': contact
      }
 
      path = os.path.join(os.path.dirname(__file__), 'plain_site.html')
      self.response.out.write(template.render(path, template_values))


class MainPage(webapp.RequestHandler):
  def get(self):

      curr_user = users.get_current_user()
      contacts_query = Contact.all()
      contacts_query.filter("user =", users.get_current_user())
      #contacts_query.order('-date')
      contacts = contacts_query.fetch(10)

      if curr_user:
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
      else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'
    
      template_values = {
       'theme_id_base': 'http://'+CONST_CSS_SERVICE+'/admin/style/base.css',
       'theme_id_tabs': 'http://'+CONST_CSS_SERVICE+'/admin/style/tabs.css',
       'theme_id_button': 'http://'+CONST_CSS_SERVICE+'/admin/style/button.css',
       'host': os.environ['HTTP_HOST'],
       'user': curr_user,
       'contacts': contacts,
       'url': url,
       'url_linktext': url_linktext,
      }
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

# Our Image Finding Libraries 
# Find Images for a Given Site Profile

def findImages(id):
  result = db.GqlQuery("SELECT * FROM Image WHERE referenceKey = :1 LIMIT 10", id).fetch(10)
  if (len(result) > 0):
    return result
  else:
    return None

def findImage(key):
  dbKey = db.Key(key)
  result = db.get(dbKey)
  if (result):
    return result
  else:
    return None

class loadImage(webapp.RequestHandler):
  def get(self):
    key = self.request.get('key')
    image = findImage(key)
    if (image and image.graphic):
      self.response.headers['Content-Type'] = 'image/jpg'
      self.response.out.write(image.graphic)
    else:
      self.redirect('/static/noimage.jpg')

# This is general page after user creates the basic entry 
# User can edit and add things here. 

class Edit_Site(webapp.RequestHandler):
  def get(self):

    curr_user = users.get_current_user()

    contacts_query = Contact.all()
    contacts_query.filter("shortname =", self.request.get('site') )
    #contacts = contacts_query.fetch(1)
    # We just want the first result
    contact_obj = contacts_query.get()

    if curr_user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    # We search for all images for this user...
    # We may change this because we may simply accept only one.

    mainObjectKey = str(contact_obj.key())
    images    = findImages(mainObjectKey)

    template_values = {

      'host': os.environ['HTTP_HOST'],
      'theme_id_base'   : 'http://'+CONST_CSS_SERVICE+'/admin/style/base.css',
      'theme_id_tabs'   : 'http://'+CONST_CSS_SERVICE+'/admin/style/tabs.css',
      'theme_id_button' : 'http://'+CONST_CSS_SERVICE+'/admin/style/button.css',
      'receipt_image'   : self.request.get('receipt_image'), # this works if this page is a return from a update / upload image check Add_Picture

      'user_images'    : images,     
      'user'        : curr_user,
      'url_domain_public': CONST_SITE_SERVICE,
      'contact_obj': contact_obj,
      'entry_key'  : str(contact_obj.key()) ,
      'url': url,
      'url_linktext': url_linktext,

    }

    path = os.path.join(os.path.dirname(__file__), 'edit_site.html')
    self.response.out.write(template.render(path, template_values))

# The page that you can create a new site - basic new account setup
class New_Profile(webapp.RequestHandler):
  def get(self):
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
      path = os.path.join(os.path.dirname(__file__), 'admin_new_profile.html')
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      path = os.path.join(os.path.dirname(__file__), 'login_needed.html')
    template_values = {
      'host': os.environ['HTTP_HOST'],
       'theme_id_base': 'http://'+CONST_CSS_SERVICE+'/admin/style/base.css',
       'theme_id_tabs': 'http://'+CONST_CSS_SERVICE+'/admin/style/tabs.css',
       'theme_id_button': 'http://'+CONST_CSS_SERVICE+'/admin/style/button.css',
      'url': url,
      'url_linktext': url_linktext,
      }
    self.response.out.write(template.render(path, template_values))

class Create_Profile(webapp.RequestHandler):
  def post(self):
     
    curr_user = users.get_current_user()

    if curr_user:
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    contact = Contact(name=self.request.get('name'))

    if curr_user:
      contact.user = curr_user

    contact.content   = self.request.get('content')
    contact.shortname = self.request.get('shortname')
    contact.theme_id  = self.request.get('theme_id')
    contact.put()

    template_values = {
       'entry_key': str(contact.key()), # we send the key of this 
       'theme_id_base': 'http://'+CONST_CSS_SERVICE+'/admin/style/base.css',
       'theme_id_tabs': 'http://'+CONST_CSS_SERVICE+'/admin/style/tabs.css',
       'theme_id_button': 'http://'+CONST_CSS_SERVICE+'/admin/style/button.css',
       'url_main_admin': 'http://admin'+CONST_SITE_SERVICE+"",
       'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'create_profile_results.html')
    self.response.out.write(template.render(path, template_values))

# WARNING bug fix to make a search if there is a picture in the db before
# This redirects 
class Add_Picture(webapp.RequestHandler):
  def post(self):

    imageinfo = Image()

    imageinfo.referenceKey  = str(self.request.get("key"))
    imageinfo.graphic       = db.Blob(images.resize(self.request.get("graphic"), 320, 240))

    site_parent = db.get(imageinfo.referenceKey)
    site_parent_shortname = site_parent.shortname

    imageinfo.put()
    self.redirect('/editar?site='+site_parent_shortname + '&receipt_image='+ str(imageinfo.key()) )

apps_binding = []

apps_binding.append(('/',                MainPage))
apps_binding.append(('/novo_site',       New_Profile))
apps_binding.append(('/show',            Plain_Show))
apps_binding.append(('/editar_imagem',   Add_Picture))
apps_binding.append(('/site_criado',  Create_Profile))
apps_binding.append(('/editar',       Edit_Site))

# These functions, http-based are callect from the HTML sometimes, so user do not see these URLs 
apps_binding.append(('/load_image',    loadImage))

# we had this before to send parameters like app/1111, app/1112 to the method
#apps_binding.append((r'/(.*)',        ProxyShowTheme))

#http://code.google.com/appengine/docs/python/tools/webapp/wsgiapplicationclass.html

application = webapp.WSGIApplication( apps_binding, debug=True)

#application = webapp.WSGIApplication( [('/', MainPage), ('/sign', AddContact)], debug=True)

def main():
  run_wsgi_app(application)
  #run_wsgi_app(applications[os.environ['HTTP_HOST']])


if __name__ == "__main__":
  main()
