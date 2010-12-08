import os
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Template(db.Model):
	name    = db.StringProperty()
	user    = db.UserProperty()
	# number  = db.StringProperty()
	# theme_id  = db.StringProperty()
	# content = db.StringProperty(multiline=True)
	# date    = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()

		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
				
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
		
		template_values = {
			'url': url,
			'url_linktext': url_linktext,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

class DashBoard(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
		if user:
			url = users.create_logout_url(self.request.uri)
			url_linktext = 'Logout'
        
		else:
			url = users.create_login_url(self.request.uri)
			url_linktext = 'Login'
			self.redirect(users.create_login_url(self.request.uri))
		
		template_values = {
			'url': url,
			'url_linktext': url_linktext,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/dashboard.html')
		self.response.out.write(template.render(path, template_values))

class ChooseGrid(webapp.RequestHandler):
	def get(self):
		
		template_values = {
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/choose-grid.html')
		self.response.out.write(template.render(path, template_values))

class EditKiosk(webapp.RequestHandler):
	def get(self):

		template_values = {
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/choose-grid.html')
		self.response.out.write(template.render(path, template_values))

class ShowKiosk(webapp.RequestHandler):
	def get(self, kiosk_number):

		template_values = {
			'kiosk_number': kiosk_number,
			}

		path = os.path.join(os.path.dirname(__file__), 'templates/show-kiosk.html')
		self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([
										('/', MainPage),
										('/dashboard', DashBoard),
										('/choose_grid', ChooseGrid),
										('/edit_kiosk', EditKiosk),
										(r'/kiosk/(.*)', ShowKiosk)
									], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()