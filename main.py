#!/usr/bin/env python

import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Contact(db.Expando):
	''' User data model '''
	pid = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	email = db.EmailProperty(required=True)
	nric = db.StringProperty(required=True)
	remark = db.TextProperty()

class MainHandler(webapp2.RequestHandler):
	''' Home page handler '''
	
	def get(self):
		''' Show home page '''
        # check if valid Google account
		user = users.get_current_user()

		if user:	# if valid logged in user
			# logout link
			url = users.create_logout_url(self.request.uri)
			# logout text
			url_linktext = 'logout'
			# retrieve user record
			query = Contact.gql('WHERE pid = :1', user.nickname())
			# get 1 record
			result = query.fetch(1)
			if result:	# if user record found
				contact = result[0]
				greeting = ("Welcome %s!" % (contact.name,))
			else:		# not found
				contact = "Invalid dhs.sg user"
				greeting = "Try again"
			
		else: 		# not logged in
			# login link
			url = users.create_login_url(self.request.uri)
			# login text
			url_linktext = 'login'	
			contact = "Not authorized"
			greeting = "You need to"
		
		template_values = {
			'contact': contact,
			'greeting': greeting,
			'url': url,
			'url_linktext': url_linktext
		}
		
		# create index.html template
		template = jinja_environment.get_template('index.html')
		# associate template values with template
		self.response.out.write(template.render(template_values))

		
class UpdateHandler(webapp2.RequestHandler):
	''' Update contact '''
	def post(self):
		if self.request.get('update'):
			# get data from form controls
			updated_name = self.request.get('name')
			updated_email = self.request.get('email')
			updated_remark = self.request.get('remark')
			updated_nric = self.request.get('nric')
			# get user to update
			user = users.get_current_user()
			query = Contact.gql('WHERE pid = :1', user.nickname())
			result = query.fetch(1)
			if result:	# user found, update
				contact = result[0]
				contact.name = updated_name
				contact.email = updated_email
				contact.remark = db.Text(updated_remark)
				contact.nric = updated_nric
				contact.put()
			else:		# user not found, error
				self.response.out.write('Update failed!')
		# go back to home page	
		self.redirect('/')

class layout(webapp2.RequestHandler):
        '''layout page'''
	def get(self):
		''' Show home page '''
        # check if valid Google account
		user = users.get_current_user()

		if user:	# if valid logged in user
			# logout link
			url = users.create_logout_url(self.request.uri)
			# logout text
			url_linktext = 'logout'
			# retrieve user record
			query = Contact.gql('WHERE pid = :1', user.nickname())
			# get 1 record
			result = query.fetch(1)
			if result:	# if user record found
				contact = result[0]
				greeting = ("Welcome %s!" % (contact.name,))
			else:		# not found
				contact = "Invalid dhs.sg user"
				greeting = "Invalid"
			
		else: 		# not logged in
			# login link
			url = users.create_login_url(self.request.uri)
			# login text
			url_linktext = 'login'	
			contact = "Not authorized"
			greeting = "You need to"
		
		template_values = {
			'contact': contact,
			'greeting': greeting,
			'url': url,
			'url_li nktext': url_linktext
		}
		
		# create index.html template
		template = jinja_environment.get_template('layout.html')
		# associate template values with template
		self.response.out.write(template.render(template_values))
		
# main
 #               contact1 = Contact(pid='toh.zijie', name='Toh Zi Jie', email='toh.zijie@dhs.sg', nric = 'S1234567D', remark = '')
#                contact1.put()
app = webapp2.WSGIApplication([('/contact', MainHandler), ('/', layout), ('/update', UpdateHandler)],
                              debug=True)

							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
							  
