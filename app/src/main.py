#!/usr/bin/env python

import webapp2
import json

from handlers import BaseJsonResponseHandler, AuthenticatedJsonHandler
from config import *
from google.appengine.ext import ndb
from models import *
from google.appengine.api import users
from google.appengine.api import search
from google.appengine.datastore.datastore_query import Cursor


def parseMeta(meta_json, meta_obj):
    for m in meta_json:
        if isinstance(m['value'], list) or isinstance(m['value'], dict):
            meta_obj.set_json_prop(m['key'], m['value'], indexed=True)
        else:
            meta_obj.set_generic_prop(m['key'], m['value'])


def createObject():
    return BaseModel(created_by_id=users.get_current_user().email(), modified_by_id=users.get_current_user().email())

def createIndexableObject():
    return IndexedObjectModel(created_by_id=users.get_current_user().email(), modified_by_id=users.get_current_user().email())

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class SearchHandler(AuthenticatedJsonHandler):
    def get(self, query, cursor=None):
        try:
            response = dict(results=[])
            if cursor is not None:
                results, next_curs, more = ndb.gql(query).fetch_page(DEFAULT_SEARCH_RESULTS_LIMIT, start_cursor=Cursor(urlsafe=cursor))
            else:
                results, next_curs, more = ndb.gql(query).fetch_page(DEFAULT_SEARCH_RESULTS_LIMIT)
            for result in results:
                response['results'].append(result.to_dict())

            if more and next_curs:
                response['next'] = next_curs.urlsafe()

        except search.Error:
            logging.exception('Search failed')

        self.render_json(response)


class MetaHandler(BaseJsonResponseHandler):
    def post(self, itemid):
        meta_json = json.loads(self.request.get('data'))
        obj = ndb.Key(urlsafe=itemid).get()
        if obj:
            meta = obj.meta
            if meta is None:
                meta = Meta()
            parseMeta(meta_json, meta)
            obj.meta = meta
            obj.put()
        self.render_json(obj.to_dict())

class ObjectHandler(AuthenticatedJsonHandler):
    def get(self, objectid):
        obj = ndb.Key(urlsafe=objectid).get()
        if obj is None:
            self.abort(404)
        else:
            self.render_json(obj.to_dict())

    def post(self, objectid=None):
        jsn = json.loads(self.request.get('obj'))
        if objectid is None:
            obj = createObject()
            data = Meta()
        else:
            obj = ndb.Key(urlsafe=objectid).get()
            data = obj.data

        if 'data' in jsn:
            parseMeta(jsn['data'],data)
            obj.data = data

        obj.put()
        self.render_json(obj.to_dict())

    def delete(self, objectid):
        ndb.Key(urlsafe=objectid).delete()

class IndexableObjectHandler(AuthenticatedJsonHandler):
    def get(self, objectid):
        obj = ndb.Key(urlsafe=objectid).get()
        if obj is None:
            self.abort(404)
        else:
            self.render_json(obj.to_dict())

    def post(self, objectid=None):
        jsn = json.loads(self.request.get('obj'))
        if objectid is None:
            obj = createIndexableObject()
            logging.info(obj)
            data = Meta()
        else:
            obj = ndb.Key(urlsafe=objectid).get()
            data = obj.data

        if 'data' in jsn:
            parseMeta(jsn['data'],data)
            obj.data = data

        obj.put()
        self.render_json(obj.to_dict())

    def delete(self, objectid):
        ndb.Key(urlsafe=objectid).delete()

class ListObjectsHandler(BaseJsonResponseHandler):
    def get(self, cursor=None):
        response = dict(results=[])
        if cursor is not None:
            results, next_curs, more = BaseModel.query().fetch_page(DEFAULT_SEARCH_RESULTS_LIMIT, start_cursor=Cursor(urlsafe=cursor))
        else:
            results, next_curs, more = BaseModel.query().fetch_page(DEFAULT_SEARCH_RESULTS_LIMIT)

        for o in results:
            response['results'].append(o.to_dict())

        if more and next_curs:
            response['next'] = next_curs.urlsafe()

        self.render_json(response)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    webapp2.Route(r'/ntntn/search/<query>/<cursor>',    handler=SearchHandler),
    webapp2.Route(r'/ntntn/search/<query>',             handler=SearchHandler),   
    webapp2.Route(r'/ntntn/objs',                       handler=ListObjectsHandler),
    webapp2.Route(r'/ntntn/obj',                        handler=ObjectHandler),
    webapp2.Route(r'/ntntn/idx',                        handler=IndexableObjectHandler),
    webapp2.Route(r'/ntntn/obj/<objectid>',             handler=ObjectHandler),
    webapp2.Route(r'/ntntn/meta/<itemid>',              handler=MetaHandler)


], debug=True)
