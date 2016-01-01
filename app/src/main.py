#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# import logging
from handlers import BaseJsonResponseHandler, AuthenticatedJsonHandler
from config import *
from google.appengine.ext import ndb
from models import *

import webapp2
import json
# import mimetypes

# from webapp2_extras import jinja2
# from directory_api_client import service

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
            # self.render_json({})
        else:
            self.render_json(obj.to_dict())

    def post(self, objectid=None):
        jsn = json.loads(self.request.get('obj'))
        if objectid is None:
            obj = createObject()
            # product.barcode_number = prod_json['barcode_number'] if 'barcode_number' in prod_json else None
            # product.barcode_format = prod_json['barcode_format'] if 'barcode_format' in prod_json else None
            data = Meta()
        else:
            obj = ndb.Key(urlsafe=objectid).get()
            # product.name = prod_json['name']
            # product.base_cost = prod_json['default_cost']
            # product.barcode_number = prod_json['barcode_number'] if 'barcode_number' in prod_json else None
            # product.barcode_format = prod_json['barcode_format'] if 'barcode_format' in prod_json else None
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
    webapp2.Route(r'/ntntn/obj/<objectid>',             handler=ObjectHandler),
    webapp2.Route(r'/ntntn/meta/<itemid>',              handler=MetaHandler)


], debug=True)
