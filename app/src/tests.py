import webapp2
import webtest
import unittest
import main
import os
import logging
import json

from google.appengine.ext import testbed
from webtest import TestApp

from models import BaseModel


def createObject(test, obj):
    test.testapp.post('/ntntn/obj', dict(obj=json.dumps(obj)))

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.testapp = webtest.TestApp(main.app)
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(USER_EMAIL='trinity@mentalpad.net', USER_ID='1', USER_IS_ADMIN='0')
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_search_stub()

    def tearDown(self):
        self.testbed.deactivate()


class TestObjectPersistence(BaseTest):

    def testCreate(self):
        response = self.testapp.post('/ntntn/obj', dict(obj=json.dumps({
            'data': [{
                'key': 'foo',
                'value': [1, 2, 3]
            }]})
        ))
        computed_id = response.json['computed_id']
        self.assertFalse(computed_id is None)

        response = self.testapp.get('/ntntn/obj/' + computed_id)
        self.assertTrue(response.json['data'] is not None)
        self.assertTrue(response.json['data']['foo'] is not None)
        self.assertTrue(len(response.json['data']['foo']) is 3)

        response = self.testapp.post('/ntntn/obj/' + computed_id, dict(obj=json.dumps({
            'data': [{
                'key': 'foo',
                'value': [1, 2, 3, 4, 5]
            }]})
        ))
        self.assertTrue(len(response.json['data']['foo']) is 5)

class TestIndexableObject(BaseTest):
    def testCreate(self):
        response = self.testapp.post('/ntntn/idx', dict(obj=json.dumps({
            'data': [{
                'key': 'indexable!',
                'value': [1, 2, 3]
            }]})
        ))
        print response
        computed_id = response.json['computed_id']
        self.assertFalse(computed_id is None)
    
class TestObjectDelete(BaseTest):

    def testDelete(self):
        response = self.testapp.post('/ntntn/obj', dict(obj=json.dumps({
            'data': [{
                'key': 'foo',
                'value': [1, 2, 3]
            }]})
        ))
        computed_id = response.json['computed_id']
        self.assertFalse(computed_id is None)
        response = self.testapp.delete('/ntntn/obj/' + computed_id)
        response = self.testapp.get('/ntntn/obj/' + computed_id, status=404)


class TestListObjects(BaseTest):
    def testCreate(self):

        i = 0
        maximum = 10

        while i < maximum:
            createObject(self, {'data': [{'key': 'foo', 'value': [i]}]})
            i += 1

        response = self.testapp.get('/ntntn/objs')
        self.assertTrue(len(response.json['results']) is maximum)


class TestSearchObjects(BaseTest):
    def testCreate(self):

        i = 0
        maximum = 10

        while i < maximum:
            createObject(self, {'data': [{'key': 'name', 'value': {'first': 'nancy %s' % i }}]})
            i += 1

        response = self.testapp.get('/ntntn/search/select * from BaseModel')
        self.assertTrue(len(response.json['results']) is maximum)
        # print response

        response = self.testapp.get('/ntntn/search/select computed_id, data.name from BaseModel')
        print response
        self.assertTrue(len(response.json['results']) is 10)





