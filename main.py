import os
import pickle
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.util import login_required

class Contact(db.Model):
	user = db.UserProperty()
	about = db.StringProperty(multiline=True)
	date = db.DateTimeProperty(auto_now_add=True)
	
class Grid(db.Model):
	name = db.StringProperty()
	grid_id = db.StringProperty()
	
class Kiosk(db.Model):
	creator	= db.ReferenceProperty(Contact,collection_name="creator_ref")
	grid = db.ReferenceProperty(Grid,collection_name="grid_ref")
	widgets = db.Blob() #pickled object for a dict like: my_widgets = {'container-1': 'clock', 'container-3': 'dumy'}

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			self.redirect('/dashboard')

		url = users.create_login_url(self.request.uri)
		url_linktext = 'Login'
		
		template_values = {
			'url': url,
			'url_linktext': url_linktext,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

class DashBoard(webapp.RequestHandler):
	@login_required
	def get(self):
		user = users.get_current_user()
		user_nickname = user.nickname()
		url = users.create_logout_url(self.request.uri)
		url_linktext = 'Logout'
		
		kiosks = Kiosk.all()
		kiosks.filter("creator.user =", user)
        
		template_values = {
			'kiosks': kiosks,
			'nickname': user_nickname,
			'url': url,
			'url_linktext': url_linktext,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
		self.response.out.write(template.render(path, template_values))

class ChooseGrid(webapp.RequestHandler):
	@login_required
	def get(self):
		
		grids = Grid.all()
		
		template_values = {
			'grids': grids,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/choose-grid.html')
		self.response.out.write(template.render(path, template_values))

# class CreateKiosk(webapp.RequestHandler):
# 	@login_required
# 	def post(self):
		


class EditKiosk(webapp.RequestHandler):
	@login_required
	def get(self):

		template_values = {
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/choose-grid.html')
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		self.redirect('/dashboard')

class ShowKiosk(webapp.RequestHandler):
	def get(self, kiosk_id):
		kiosk = Kiosk.all()
		kiosk.filter("key_name =", kiosk_id)

		template_id = kiosk.grid.grid_id
		widgets = {}
		
		template_values = {
			'kiosk_id': kiosk_id,
			}

		path = os.path.join(os.path.dirname(__file__), 'grids/template'+ template_id +'.html')
		self.response.out.write(template.render(path, template_values))

# just in development environment to insert template, must be moved to /admin
class Feeder(webapp.RequestHandler):
	@login_required
	def get(self):

		grid = Grid(name="4x4", grid_id="1")
		grid.put()
		
		self.response.out.write("models created")

application = webapp.WSGIApplication([
										('/', MainPage),
										('/dashboard', DashBoard),
										('/choose_grid', ChooseGrid),
										('/edit_kiosk', EditKiosk),
										(r'/kiosk/(.*)', ShowKiosk),
										# ('/feeder', Feeder)
									], debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()