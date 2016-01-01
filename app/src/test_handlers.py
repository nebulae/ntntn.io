from handlers import AdminAuthenticatedTemplateHandler
import webapp2
from google.appengine.api import memcache, app_identity, users

class MainHandler(AdminAuthenticatedTemplateHandler):
    def get(self):
        template_vals = {}
        template_vals['users'] = users
        self.render_template("tests.html", template_vals)

app = webapp2.WSGIApplication([
    ('/tests', MainHandler),
    ('/tests/', MainHandler),
], debug=True)
