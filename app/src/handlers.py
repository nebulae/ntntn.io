import os
import webapp2
import jinja2
import json
import logging

import datetime
from time import mktime
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.api import search
from google.appengine.ext import ndb

from decimal import *

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'),
    extensions=['jinja2.ext.autoescape'])

class CustomJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime.datetime):
            return long(mktime(obj.timetuple()))
        if isinstance(obj, ndb.Key):
            return str(obj.urlsafe())
        if isinstance(obj, ndb.GeoPt):
            return {'lat': obj.lat, 'lon': obj.lon}
        if isinstance(obj, search.GeoPoint):
            return {'lat': obj.latitude, 'lon': obj.longitude}
        if isinstance(obj, ndb.BlobProperty):
            return True if obj is not None else False
        return json.JSONEncoder.default(self, obj)

#
# Base Class for all requests which redirect to a template.
#
class BaseTemplateHandler(webapp2.RequestHandler):
    
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, filename, template_args):
        template = JINJA_ENVIRONMENT.get_template(filename)
        if users.get_current_user():
            logout_url = users.create_logout_url('/')
            template_args['auth_url'] = logout_url
            template_args['user'] = users.get_current_user()
            template_args['auth_text'] = ''
        else: 
            template_args['auth_url'] = users.create_login_url(dest_url='/')
            template_args['auth_text'] = '<img src="image/dt-login.png" />'
        self.response.write(template.render(template_args))


#
# Base Class for all requests that redirect to a template and require authentication.
#
class AuthenticatedTemplateHandler(BaseTemplateHandler):
    def dispatch(self):
        user = users.get_current_user()
        if user:
            super(AuthenticatedTemplateHandler, self).dispatch()
        else:
            self.redirect('/')

#
# Base Class for all requests that redirect to a template and require administrative authentication.
#
class AdminAuthenticatedTemplateHandler(BaseTemplateHandler):
    def dispatch(self):
        admin = users.is_current_user_admin()
        if admin:
            super(AdminAuthenticatedTemplateHandler, self).dispatch()
        else:
            self.redirect('/')

#
# Base Class for all requests which need a json response.
#
class BaseJsonResponseHandler(webapp2.RequestHandler):
    def render_json(self, dict):
        callback = self.request.get('callback')
        self.response.headers['Content-Type'] = 'application/json'
        if callback:
            self.response.out.write('{0}({1})'.format(callback, json.dumps(dict, cls=CustomJsonEncoder)))
        else: 
            self.response.out.write(json.dumps(dict, cls=CustomJsonEncoder))
#
# Base Class for all requests which need a json response and require authentication.
#
class AuthenticatedJsonHandler(BaseJsonResponseHandler):
    def dispatch(self):
        user = users.get_current_user()
        if user:
            super(AuthenticatedJsonHandler, self).dispatch()
        else:
            self.abort(401, detail="You must be an authenticated user to access this resource.")

#
# Base Class for all requests which need a json response and require administrative authentication.
#
class AdminAuthenticatedJsonHandler(BaseJsonResponseHandler):
    def dispatch(self):
        admin = users.is_current_user_admin()
        if admin:
            super(AdminAuthenticatedJsonHandler, self).dispatch()
        else:
            self.abort(401, detail="You must be an authenticated administrator to access this resource.")


