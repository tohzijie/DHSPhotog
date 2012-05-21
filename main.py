#!/usr/bin/env python

import webapp2	# web application framework
import jinja2	# template engine
import os		# access file system
from google.appengine.api import users	# Google account authentication
from google.appengine.ext import db		# datastore
import cgi
import datetime
import urllib

# initialize template
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class Contact(db.Expando):
	''' User data model '''
	pid = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	class1 =db.StringProperty(required=True)
	email = db.EmailProperty(required=True)
	nric = db.StringProperty(required=True)
	nric1=db.StringProperty(required=False)
	camera=db.StringProperty(required=False)
	tel = db.StringProperty(required=True)
	tel1=db.StringProperty(required=False)
	lens=db.StringProperty(required=True)
	purpose = db.StringProperty(required=True)
	remark = db.TextProperty()
	date = db.DateTimeProperty(auto_now_add = True)        

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
				greeting = ("Hello %s! Not you? Please " % (contact.name,))
			else:		# not found
				contact = "Invalid dhs.sg user"
				greeting = "You are not authorise to loan"
			
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
			updated_remark = self.request.get('remark')
			updated_nric = self.request.get('nric')
			updated_camera=self.request.get('camera')
			updated_lens=self.request.get('lens')
			updated_tel=self.request.get('tel')
			updated_purpose=self.request.get('purpose')
			# get user to update
			user = users.get_current_user()
			query = Contact.gql('WHERE pid = :1', user.nickname())
			result = query.fetch(1)
                        contact=result[0]
			if result and updated_nric==str(contact.nric1) and updated_tel==str(contact.tel1):	# user found, update
#				contact = result[0]
				contact.remark = db.Text(updated_remark)
				contact.nric = updated_nric
				contact.camera = updated_camera
				contact.purpose=updated_purpose
				contact.lens = updated_lens
				contact.put()
				self.response.write('''<!DOCTYPE html><html><head> Your request has been saved. Thank you!</head><body>
<form method="LINK" action="/">
<input type="submit" value="Home">
</form></html>''')
			else:		# user not found, error
				self.response.out.write('''<!DOCTYPE html><html><head>Update failed! Please try again.</head>
                                                        <body><form method="LINK" action="/loan"><input type="submit" value="Back">
</form></html>''')
				return
		# go back to home page	
#		self.redirect('/')

class Greeting(db.Model):
        """Models an individual Guestbook entry with an author, content, and date."""
        author = db.UserProperty()
        content = db.StringProperty(multiline=True)
        date = db.DateTimeProperty(auto_now_add=True)



def guestbook_key(guestbook_name=None):
          return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

class GuestMain(webapp2.RequestHandler):
        def get(self):
                user = users.get_current_user()
                self.response.out.write('<html><head> <form method = "LINK" action="/" align="left"><input type ="submit" value = "Home"></form><body>')
                guestbook_name=self.request.get('guestbook_name')

    # Ancestor Queries, as shown here, are strongly consistent with the High
    # Replication Datastore. Queries that span entity groups are eventually
    # consistent. If we omitted the ancestor from this query there would be a
    # slight chance that Greeting that had just been written would not show up
    # in a query.
                greetings = Greeting.gql("WHERE ANCESTOR IS :1 ORDER BY date DESC LIMIT 10",
                                        guestbook_key(guestbook_name))
		for greeting in greetings:
				if greeting.author:
						self.response.out.write(
						'<b>%s</b> wrote:' % greeting.author.nickname())
				else:
						self.response.out.write('An anonymous person wrote:')
				self.response.out.write('<blockquote>%s</blockquote>' %
										cgi.escape(greeting.content))

		self.response.out.write("""
		  <form action="/sign?%s" method="post">
			<div><textarea name="content" rows="3" cols="60"></textarea></div>
			<div><input type="submit" value="Shoot!"></div>
		  </form>
		  <hr>
		  <form>Secret Code: <input value="%s" name="guestbook_name">
		  <input type="submit" value="switch"></form>
		  <p align="right">&copy;TZJ</p>
		</body>
	  </html>""" % (urllib.urlencode({'guestbook_name': guestbook_name}),
						  cgi.escape(guestbook_name.lower())))

class Guestbook(webapp2.RequestHandler):
        def post(self):
                guestbook_name = self.request.get('guestbook_name')
                greeting = Greeting(parent=guestbook_key(guestbook_name))
                if users.get_current_user():
                        greeting.author = users.get_current_user()

                greeting.content = self.request.get('content')
                greeting.put()
                self.redirect('/GuestMain?' + urllib.urlencode({'guestbook_name': guestbook_name}))

class about(webapp2.RequestHandler):
        def get(self):
		self.response.out.write('''
                                <!Doctype HTML><html>
<head>
<meta charset="UTF-8">
</head>
<body bgcolor=black>
<font color="white"><u><h1>About
</h1></u>
<p>This app is proudly borught to you by </p>
<h1> <font color="#FF0000">TOH ZI JIE</font></h1>
<p>Class: 5C23 </p>
<p>Email: <a href="mailto:"toh.zijie@dhs.sg">toh.zijie@dhs.sg </a> </p>
<p align="right">&copy;TZJ</p>
</font>
</body>
</html>''')


                


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
				greeting = "You are not authorise to loan"
			
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
		template = jinja_environment.get_template('layout.html')
		# associate template values with template
		self.response.out.write(template.render(template_values))
		
# main
#                contact1 = Contact(pid='toh.zijie', name='Toh Zi Jie', purpose='Nil', email='toh.zijie@dhs.sg', class1="5C23", tel1 ='61234567',tel="61234567", camera="None", nric1="S1234567D",nric="S1234567D", lens="None", remark = '')
#                contact1.put()
#                contact2=Contact(pid='lim.ahseng', name='Lim Ah Seng', purpose='Nil', email='lim.ahseng@dhs.sg', class1="5C99", tel1='61234567', tel='61234567', camera="None", nric1="S1234567D",nric="S1234567D", lens="None", remark = '')
#                contact2.put()                 
app = webapp2.WSGIApplication([('/loan', MainHandler), ('/', layout), ('/update', UpdateHandler), ('/about', about),('/forum', GuestMain), ('/sign', Guestbook)],
                              debug=True)

							  
							  
							  
							  
							  
							  
