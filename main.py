
import os
import pickle
import random
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

# constantst for blurb generation, probabily there is a better way to make it
BLURB_SIZE = 8
BLURB_CHARS = "abcdefghijklmnopqrstuvxywzABCDEFGHIJKLMNOPQRSTUVXYWZ0123456789"

#blurb generator, check duplicates
def generate_blurb():
	blurb = ''
	for i in range(BLURB_SIZE):
		blurb += random.choice(BLURB_CHARS)
	if (Kiosk.all().filter("blurb = ", blurb).get() == blurb):
		return generate_blurb()
	else:
		return blurb

# User information
# class Contact(db.Model):
# 	user = db.UserProperty(required=True)
# 	name = db.StringProperty()
# 	about = db.StringProperty(multiline=True)
# 	date = db.DateTimeProperty(auto_now_add=True)

# Kiosk info and widgets used
class Kiosk(db.Model):
	blurb = db.StringProperty(required=True)
	creator = db.UserProperty(required=True)
	name = name = db.StringProperty(default="My Kiosk")
	date = db.DateTimeProperty(auto_now_add=True)
	content = db.StringProperty(multiline=True) # db.Blob() #pickled object with javascript and css content for kiosk rendering


# Main Page
class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect('/dashboard')

		url = users.create_login_url(self.request.uri)
		
		template_values = {
			'url': url,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

# Dashboard, logged user
class DashBoard(webapp.RequestHandler):
	@login_required
	def get(self):
		# login information
		user = users.get_current_user()
		url = users.create_logout_url(self.request.uri)
		
		kiosks = Kiosk.all().filter("creator = ",users.get_current_user()).order('-date')
		# contact.filter("user =", user)
		# kiosks.filter("creator =", contact)
		blurb = generate_blurb()

        
		template_values = {
			'kiosks': kiosks,
			'url': url,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
		self.response.out.write(template.render(path, template_values))

# Handler to create a kiosk and redirect to Edit Kiosk Handler
class CreateKiosk(webapp.RequestHandler):
	@login_required
	def get(self):
		blurb = generate_blurb()
		kiosk = Kiosk(creator=users.get_current_user(), blurb = blurb)
		kiosk.put()
		
		self.redirect('/edit/'+blurb)

# Page where user is able to edit and add widgets
class EditKiosk(webapp.RequestHandler):
	@login_required
	def get(self, kiosk_id):
		#request kiosk
		kiosk = Kiosk.all().filter("blurb =", kiosk_id).get()
		# if there is no kiosk go to home page
		if not kiosk:
			self.redirect('/')
		
		template_values = {
			'kiosk': kiosk,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/edit-kiosk.html')
		self.response.out.write(template.render(path, template_values))

# Save edited kiosk
class SaveKiosk(webapp.RequestHandler):
	def post(self):
		kiosk = Kiosk.all().filter("blurb =", self.request.get('blurb')).get()
		kiosk.name = self.request.get('name')
		kiosk.content = self.request.get('content')
		kiosk.put()
		# self.request.get('content')
		self.redirect('/')

# Kiosk, final view, public
class ShowKiosk(webapp.RequestHandler):
	def get(self, kiosk_id):
		#request kiosk
		kiosk = Kiosk.all().filter("blurb =", kiosk_id).get()
		# if there is no kiosk go to home page
		if not kiosk:
			self.redirect('/')
		
		template_values = {
			'kiosk': kiosk,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/show-kiosk.html')
		self.response.out.write(template.render(path, template_values))

# urlconf
application = webapp.WSGIApplication([
										('/', MainPage),
										('/dashboard', DashBoard),
										('/create', CreateKiosk),
										('/save', SaveKiosk),
										(r'/edit/(.*)', EditKiosk),
										(r'/kiosk/(.*)', ShowKiosk),
									], debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()