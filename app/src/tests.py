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

ownerid = None

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


class TestObjectSearch(BaseTest):
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


# class DogtopiaUnitTest(unittest.TestCase):
#     def setUp(self):
#         self.testapp = webtest.TestApp(services.app)
#         self.testbed = testbed.Testbed()
#         self.testbed.setup_env(USER_EMAIL='fran1emp1@i-spos.com',USER_ID='1', USER_IS_ADMIN='0')
#         self.testbed.activate()
#         self.testbed.init_datastore_v3_stub()
#         self.testbed.init_memcache_stub()    
#         self.testbed.init_search_stub()    

#         #for all the tests, prepopulate the org units
#         orgunits_response = self.testapp.get('/services/directoryapi/orgunits')
#         self.assertFalse(orgunits_response is None)
#         for ou in orgunits_response.json['organizationUnits']:
#             ou_response = self.testapp.post('/services/orgunit', dict(ou=json.dumps(ou)))

#         print "\n"
#         print "DONE ADDING ORG UNITS"
#         print "--------------------------------------------"

#     def tearDown(self):
#         self.testbed.deactivate()

#     def addProductToFranchise(self, name, price):
#         pass

#     def addServiceToFranchise(self, name, price):

#         user = self.testapp.get('/services/user/fran1emp1@i-spos.com')
#         franchise_id = user.json['orgunit']['computed_id']

#         response = self.testapp.post('/services/service', dict(service=json.dumps({
#             'name': name, 
#             'default_cost': price
#             })
#         ))
#         computed_id = response.json['computed_id']

#         response = self.testapp.post('/services/franchise/%s/service' % franchise_id, 
#             dict(service=json.dumps({
#                 'serviceid' : computed_id, 
#                 'cost_override' : price
#             })))

#         return response.json['computed_id']

#     def addProductToFranchise(self, name, price):
#         user = self.testapp.get('/services/user/fran1emp1@i-spos.com')
#         franchise_id = user.json['orgunit']['computed_id']

#         #add a global product
#         response = self.testapp.post('/services/product', dict(product=json.dumps({
#             'name': name, 
#             'default_cost': price})
#         ))

#         #get the id of the global product created
#         computed_id = response.json['computed_id']

#         response = self.testapp.post('/services/franchise/%s/product' % franchise_id, 
#             dict(product=json.dumps({
#                 'productid' : computed_id, 
#                 'cost_override' : price
#             })))

#         return response.json['computed_id']




# class FranchiseServiceTest(DogtopiaUnitTest):
    
#     def testFranchiseServiceHandler(self):
#         #get the user
#         print "\n"
#         print "GETTING USER"
#         print "--------------------------------------------"

#         user = self.testapp.get('/services/user/fran1emp1@i-spos.com')
#         self.assertFalse(user is None)
#         # print user

#         #get the franchise from the user response
#         franchise_id = user.json['orgunit']['computed_id']
#         self.assertFalse(franchise_id is None)
#         print "\n"
#         print "GOT FRANCHISE FOR USER"
#         print franchise_id
#         print "--------------------------------------------"

#         #add a global service
#         response = self.testapp.post('/services/service', dict(service=json.dumps({
#             'name': 'test service', 
#             'default_cost': 400.00})
#         ))

#         #get the id of the global service created
#         computed_id = response.json['computed_id']
#         self.assertFalse(computed_id is None)

#         # print "--------------------------------------------"

#         #asset the serice has been added
#         response = self.testapp.get('/services/services');
#         self.assertTrue(len(response.json) == 1)

#         # print "--------------------------------------------"

#         #add the global service to the franchise
#         response = self.testapp.post('/services/franchise/%s/service' % franchise_id, 
#             dict(service=json.dumps({
#                 'serviceid' : computed_id, 
#                 'cost_override' : 10.00
#             })))

#         # print "--------------------------------------------"
#         # print response
#         # print "--------------------------------------------"

#         #get the id of the franchise service just added
#         self.assertFalse(response is None)
#         franchise_service_id = response.json['computed_id']
#         self.assertFalse(franchise_service_id is None)

#         print "\n"
#         print "--------------------------------------------"
#         print "FRANCHISE SERVICE ID: %s" % franchise_service_id
#         print "--------------------------------------------"

#         #confirm that the franchise services length is > 0
#         franchise_services_response = self.testapp.get('/services/franchise/%s/services' % franchise_id)
#         self.assertFalse(len(franchise_services_response.json) < 1)

#         # print "--------------------------------------------"
#         # print "FRANCHISE SERVICES: \n%s" % franchise_services_response
#         # print "--------------------------------------------"

#         #get the franchise service we just created
#         franchise_Service_response = self.testapp.get('/services/franchise/%s/service/%s' % (franchise_id, franchise_service_id))
#         self.assertFalse(franchise_Service_response is None)
#         # print "--------------------------------------------"
#         # print "FRANCHISE SERVICE: \n%s" %franchise_Service_response
#         # print "--------------------------------------------"
#         franchise_service_id = franchise_Service_response.json['computed_id']
#         self.assertFalse(franchise_service_id is None)
#         date_modified = franchise_Service_response.json['date_modified']

#         franchise_service_update_response = self.testapp.post('/services/franchise/%s/service/%s' % (franchise_id, franchise_service_id), 
#             dict(service=json.dumps({
#                 'cost_override' : 123.45    
#             })))
#         # print "--------------------------------------------"
#         # print "FRANCHISE SERVICE UPDATE: \n%s" %franchise_service_update_response
#         # print "--------------------------------------------"

#         self.assertFalse(franchise_service_update_response is None)
#         self.assertEqual(franchise_service_update_response.json['cost_override'], 123.45)
#         # self.assertNotEqual(date_modified, franchise_service_update_response.json['date_modified'])

# class FranchiseProductTest(DogtopiaUnitTest):
    
#     def testFranchiseProductHandler(self):
#         #get the user
#         print "\n"
#         print "GETTING USER"
#         print "--------------------------------------------"

#         user = self.testapp.get('/services/user/fran1emp1@i-spos.com')
#         self.assertFalse(user is None)
#         # print user

#         #get the franchise from the user response
#         franchise_id = user.json['orgunit']['computed_id']
#         self.assertFalse(franchise_id is None)
#         print "\n"
#         print "GOT FRANCHISE FOR USER"
#         print franchise_id
#         print "--------------------------------------------"

#         #add a global product
#         response = self.testapp.post('/services/product', dict(product=json.dumps({
#             'name': 'test product', 
#             'default_cost': 400.00})
#         ))

#         #get the id of the global product created
#         computed_id = response.json['computed_id']
#         self.assertFalse(computed_id is None)

#         # print "--------------------------------------------"

#         #asset the product has been added
#         response = self.testapp.get('/services/products');
#         self.assertTrue(len(response.json) == 1)

#         # print "--------------------------------------------"

#         #add the global product to the franchise
#         response = self.testapp.post('/services/franchise/%s/product' % franchise_id, 
#             dict(product=json.dumps({
#                 'productid' : computed_id, 
#                 'cost_override' : 10.00
#             })))

#         # print "--------------------------------------------"
#         # print response
#         # print "--------------------------------------------"

#         #get the id of the franchise product just added
#         self.assertFalse(response is None)
#         franchise_product_id = response.json['computed_id']
#         self.assertFalse(franchise_product_id is None)

#         print "\n"
#         print "--------------------------------------------"
#         print "FRANCHISE PRODUCT ID: %s" % franchise_product_id
#         print "--------------------------------------------"

#         #confirm that the franchise products length is > 0
#         franchise_products_response = self.testapp.get('/services/franchise/%s/products' % franchise_id)
#         self.assertFalse(len(franchise_products_response.json) < 1)

#         # print "--------------------------------------------"
#         # print "FRANCHISE PRODUCTS: \n%s" % franchise_products_response
#         # print "--------------------------------------------"

#         #get the franchise product we just created
#         franchise_product_response = self.testapp.get('/services/franchise/%s/product/%s' % (franchise_id, franchise_product_id))
#         self.assertFalse(franchise_product_response is None)
#         # print "--------------------------------------------"
#         # print "FRANCHISE SERVICE: \n%s" %franchise_product_response
#         # print "--------------------------------------------"
#         franchise_product_id = franchise_product_response.json['computed_id']
#         self.assertFalse(franchise_product_id is None)
#         date_modified = franchise_product_response.json['date_modified']

#         franchise_product_update_response = self.testapp.post('/services/franchise/%s/product/%s' % (franchise_id, franchise_product_id), 
#             dict(product=json.dumps({
#                 'cost_override' : 123.45    
#             })))
#         # print "--------------------------------------------"
#         # print "FRANCHISE PRODUCT UPDATE: \n%s" %franchise_product_update_response
#         # print "--------------------------------------------"

#         self.assertFalse(franchise_product_update_response is None)
#         self.assertEqual(franchise_product_update_response.json['cost_override'], 123.45)

# class OwnerTest(DogtopiaUnitTest):

#     def testOwnerHandler(self):
#         print "\n"
#         owner = {
#             'people' : [{
#                 'person_type' : 'emergency contact',
#                 'first_name' : 'owner 1',
#                 'last_name' : 'owner 1 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             },{
#                 'first_name' : 'owner 2',
#                 'last_name' : 'owner 2 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             }], 
#             'signed_contract' : True,
#             'signed_boarding_agreement' : False
#         }

#         response = self.testapp.post('/services/owner',dict(owner=json.dumps(owner)))
#         # print response
#         self.assertEqual(response.status_int, 200)
#         self.ownerid = response.json['computed_id']
#         self.assertFalse(self.ownerid == None)
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(len(response.json['people']), 2)
#         self.assertEqual(response.json['modified_by_id'], "fran1emp1@i-spos.com")      
#         self.assertEqual(response.json['date_created'], response.json['date_modified'])

#         owner = {
#             'people' : [{
#                 'first_name' : 'owner 1',
#                 'last_name' : 'owner 1 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             },{
#                 'first_name' : 'owner 2',
#                 'last_name' : 'owner 2 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             },{
#                 'first_name' : 'owner 3',
#                 'last_name' : 'owner 3 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             }], 
#             'signed_contract' : False,
#             'signed_boarding_agreement' : False
#         }

#         response = self.testapp.post('/services/owner/%s' % self.ownerid, dict(owner=json.dumps(owner)))
#         self.assertEqual(response.status_int, 200)
#         self.assertEqual(response.json['computed_id'], self.ownerid)
#         self.assertFalse(self.ownerid == None)
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(len(response.json['people']), 3)
#         self.assertFalse(response.json['signed_contract'])  

#         response = self.testapp.get('/services/owners/search/owner')
#         self.assertEqual(len(response.json['results']), 3)

# class OrgUnitsTest(DogtopiaUnitTest):
#     def  testOrgUnitsListHandler(self):
#         response = self.testapp.get('/services/orgunits')
#         self.assertFalse(response is None)
#         self.assertTrue(len(response.json)>0)

# class ServicesTest(DogtopiaUnitTest):
#     def testPersonHandler(self):
#         response = self.testapp.post('/services/people', dict(first_name='trinity', last_name='harrison'))
#         self.assertEqual(response.status_int, 200)
#         # print response
#         # print("people in datastore: %s " % len(Person.query().fetch()))
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertTrue("trinity harrison" in response)

#     def testUserInfoHandler(self):
#         response = self.testapp.get('/services/user')
#         self.assertEqual(response.status_int, 200)
#         self.assertEqual(response.content_type, 'application/json')
#         self.assertEqual(response.json['email'], 'fran1emp1@i-spos.com')

#     def testDirectoryUserInfoHandler(self):
#         org_user_id = "fran1emp1@i-spos.com"
#         response = self.testapp.get('/services/user/%s' % org_user_id)
#         self.assertEqual(response.status_int, 200)
#         self.assertEqual(response.content_type, 'application/json')
#         # self.assertEqual(response.json['email'], org_user_id)

# class UsersTest(DogtopiaUnitTest):
#     def testListUsersHandler(self):
#         response = self.testapp.get('/services/users')
#         # print "--------------------------------------------"
#         # print "USERS RESPONSE: \n %s" % response 
#         # print "--------------------------------------------"
#         self.assertEqual(response.status_int, 200)
#         self.assertFalse(response is None)

# class PetHandlersTest(DogtopiaUnitTest):
#     def testPetHandlers(self):
#         print "\n"
#         print "testPetHandlers" 
#         print "--------------------------------------------"

#         #create breed
#         response = self.testapp.post('/services/breed', dict(name='test breed'))
#         self.assertEqual(response.status_int, 200)
#         self.assertFalse(response is None)
#         breed_id = response.json['computed_id']
#         self.assertFalse(breed_id is None)
#         print "\n"
#         print "created breed" 
#         print "--------------------------------------------"

#         #create owner

#         owner = {
#             'people' : [{
#                 'person_type' : 'emergency contact',
#                 'first_name' : 'owner 1',
#                 'last_name' : 'owner 1 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             },{
#                 'first_name' : 'owner 2',
#                 'last_name' : 'owner 2 lastname',
#                 'email' : ['test@email.com', 'test2@email.com'],
#                 'phone_numbers' : [{ 
#                     'phone_type' : 'home',
#                     'phone_number' : '123 456 7890'
#                 },{ 
#                     'phone_type' : 'work',
#                     'phone_number' : '123 456 7890 x3456'
#                 }], 
#                 'address':[{
#                     'address_type': 'home',
#                     'address_1' : '1234 some road',
#                     'address_2' : 'unit 1234',
#                     'city' : 'seattle',
#                     'state' : 'wa',
#                     'zip' : '98070',
#                 }]
#             }], 
#             'signed_contract' : True,
#             'signed_boarding_agreement' : False
#         }

#         response = self.testapp.post('/services/owner',dict(owner=json.dumps(owner)))
#         self.assertEqual(response.status_int, 200)
#         owner_id = response.json['computed_id']
#         self.assertFalse(owner_id is None)

#         print "\n"
#         print "created owner" 
#         print "--------------------------------------------"

#         #create pet
#         pet = {
#             'name' : 'test pet',
#             'breedid' : breed_id,
#             'ownerid': owner_id
#         }

#         response = self.testapp.post('/services/pet', dict(pet=json.dumps(pet)))
#         self.assertEqual(response.status_int, 200)
#         pet_id = response.json['computed_id']
#         self.assertFalse(pet_id is None)

#         #get pet

#         response = self.testapp.get('/services/pet/%s' % pet_id)
#         self.assertEqual(response.status_int, 200)
#         pet_id = response.json['computed_id']
#         self.assertFalse(pet_id is None)

#         #update pet
#         pet = {
#             'name' : 'test pet edited name',
#         }

#         response = self.testapp.post('/services/pet/%s' % pet_id, dict(pet=json.dumps(pet)))
#         self.assertEqual(response.status_int, 200)
#         pet_id = response.json['computed_id']
#         self.assertFalse(pet_id is None)

#         #get pet
#         response = self.testapp.get('/services/pet/%s' % pet_id)
#         self.assertEqual(response.status_int, 200)
#         pet_id = response.json['computed_id']
#         self.assertFalse(pet_id is None)
#         self.assertEqual(response.json['name'], 'test pet edited name')
#         self.assertEqual(response.json['owner']['computed_id'], owner_id)
#         self.assertEqual(response.json['breed']['computed_id'], breed_id)

#         #check in pet

#         serviceid = self.addServiceToFranchise(name='test service', price=12.00)
#         serviceid_2 = self.addServiceToFranchise(name='test service 2', price=150.00)
#         serviceid_3 = self.addServiceToFranchise(name='test service 3', price=100.00)
#         serviceid_4 = self.addServiceToFranchise(name='test service 4', price=50.00)

#         productid = self.addProductToFranchise(name='test product', price=150.00)
#         productid_2 = self.addProductToFranchise(name='test product 2', price=100.00)
#         productid_3 = self.addProductToFranchise(name='test product 3', price=1.00)
#         productid_4 = self.addProductToFranchise(name='test product 4', price=10.00)

#         checkin = {
#             'services' : [serviceid, serviceid_2],
#             'products' : [productid, productid_2, productid_3]
#         }

#         response = self.testapp.post('/services/pet/%s/checkin' % pet_id, dict(checkin=json.dumps(checkin)))
#         self.assertEqual(response.status_int, 200)
#         checkin_id = response.json['computed_id']
#         self.assertFalse(checkin_id is None)

#         self.assertEqual(len(response.json['products']), 3)
#         self.assertEqual(len(response.json['services']), 2)

#         #get checkin

#         response = self.testapp.get('/services/checkin/%s' % checkin_id)
#         self.assertEqual(response.status_int, 200)


#         checkin = {
#             'status': 'edited status', 
#             'add_products' : [ productid_4 ],
#             'add_services' : [ serviceid_4 ]
#         }

#         response = self.testapp.post('/services/checkin/%s' % checkin_id, dict(checkin=json.dumps(checkin)))
#         self.assertEqual(response.status_int, 200)

#         response = self.testapp.get('/services/checkin/%s' % checkin_id)
#         self.assertEqual(response.status_int, 200)

#         self.assertEqual(len(response.json['products']), 4)
#         self.assertEqual(len(response.json['services']), 3)

#         checkin = {
#             'status': 'edited status again', 
#             'remove_products' : [ productid, productid_2, productid_3 ],
#             'remove_services' : [ serviceid, serviceid_2 ]
#         }

#         response = self.testapp.post('/services/checkin/%s' % checkin_id, dict(checkin=json.dumps(checkin)))
#         self.assertEqual(response.status_int, 200)

#         response = self.testapp.get('/services/checkin/%s' % checkin_id)
#         self.assertEqual(response.status_int, 200)

#         self.assertEqual(len(response.json['products']), 1)
#         self.assertEqual(len(response.json['services']), 1)

#         response = self.testapp.post('/services/checkout/%s' % checkin_id)
#         self.assertEqual(response.status_int, 200)

#         response = self.testapp.get('/services/checkouts')
#         self.assertEqual(response.status_int, 200)
#         self.assertTrue(len(response.json['results'])==1)
#         self.assertEqual(response.json['results'][0]['checkin_id'], checkin_id)



# class ActivateNotesMetaTest(DogtopiaUnitTest):
#     def testActivateProductHandler(self):
#         print "\n"
#         print "testActivateProductHandler" 
#         print "--------------------------------------------"
#         #add a global product
#         response = self.testapp.post('/services/product', dict(product=json.dumps({
#             'name': 'test product', 
#             'default_cost': 400.00})
#         ))

#         print "\n"
#         print "CREATED PRODUCT" 
#         print "--------------------------------------------"

#         #get the id of the global product created
#         computed_id = response.json['computed_id']
#         self.assertFalse(computed_id is None)
#         self.assertTrue(response.json['active'])  

#         deactivate_response = self.testapp.post('/services/deactivate/%s' % computed_id)
#         self.assertEqual(deactivate_response.status_int, 200)
#         self.assertFalse(deactivate_response is None)

#         print "\n"
#         print "DEACTIVATED PRODUCT" 
#         print "--------------------------------------------"

#         product_response = self.testapp.get('/services/getobject/%s' % computed_id)
#         self.assertFalse(product_response.json['active'])

#         activate_response = self.testapp.post('/services/activate/%s' % computed_id)
#         self.assertEqual(deactivate_response.status_int, 200)
#         self.assertFalse(deactivate_response is None)

#         print "\n"
#         print "ACTIVATED PRODUCT" 
#         print "--------------------------------------------"

#         product_response = self.testapp.get('/services/getobject/%s' % computed_id)
#         self.assertTrue(product_response.json['active'])

#         meta_json = [{ 'key':'test_key', 'value': 'test_value'}]

#         meta_response = self.testapp.post('/services/meta/%s' % computed_id, dict(meta=json.dumps(meta_json)))
#         self.assertEqual(meta_response.status_int, 200)
#         self.assertFalse(meta_response is None)

#         product_response = self.testapp.get('/services/getobject/%s' % computed_id)
#         self.assertTrue(product_response.json['meta'] is not None)
#         self.assertTrue(len(product_response.json['meta']), 1)

#         print "\n"
#         print "CREATED META" 
#         print "--------------------------------------------"

#         self.assertEqual(product_response.json['meta']['test_key'], 'test_value')
#         self.assertEqual(len(product_response.json['meta']), 1)

#         meta_json = [{ 'key':'test_key', 'value': 'test_value_edited'}]

#         meta_response = self.testapp.post('/services/meta/%s' % computed_id, dict(meta=json.dumps(meta_json)))
#         self.assertEqual(meta_response.status_int, 200)
#         self.assertFalse(meta_response is None)

#         product_response = self.testapp.get('/services/getobject/%s' % computed_id)
#         self.assertTrue(product_response.json['meta'] is not None)
#         self.assertTrue(len(product_response.json['meta']), 1)
        
#         print "\n"
#         print "EDITED META" 
#         print "--------------------------------------------"

#         self.assertEqual(product_response.json['meta']['test_key'], 'test_value_edited')
#         self.assertEqual(len(product_response.json['meta']), 1)


#         meta_json = [{ 'key':'test_key_2', 'value': 'test_value_2'}]

#         meta_response = self.testapp.post('/services/meta/%s' % computed_id, dict(meta=json.dumps(meta_json)))
#         self.assertEqual(meta_response.status_int, 200)
#         self.assertFalse(meta_response is None)

#         product_response = self.testapp.get('/services/getobject/%s' % computed_id)
#         self.assertTrue(product_response.json['meta'] is not None)
#         self.assertTrue(len(product_response.json['meta']), 1)
        
#         print "\n"
#         print "CREATED MORE META" 
#         print "--------------------------------------------"

#         self.assertEqual(product_response.json['meta']['test_key_2'], 'test_value_2')
#         self.assertEqual(len(product_response.json['meta']), 2)

#         note_json = { 'text': 'this is a test note about something.' }

#         notes_response = self.testapp.post('/services/notes/%s' % computed_id, dict(text='this is a test note about something'))
#         self.assertEqual(notes_response.status_int, 200)
#         self.assertFalse(notes_response is None)

#         print "\n"
#         print "CREATED NOTE" 
#         print "--------------------------------------------"

#         notes_response = self.testapp.get('/services/notes/%s' % computed_id)
#         self.assertEqual(notes_response.status_int, 200)
#         self.assertFalse(notes_response is None)
#         self.assertTrue(len(notes_response.json) == 1)

#         notes_response = self.testapp.post('/services/notes/%s' % computed_id, dict(text='this is a test note about something'))
#         self.assertEqual(notes_response.status_int, 200)
#         self.assertFalse(notes_response is None)

#         print "\n"
#         print "CREATED ANOTHER NOTE" 
#         print "--------------------------------------------"

#         notes_response = self.testapp.get('/services/notes/%s' % computed_id)
#         self.assertEqual(notes_response.status_int, 200)
#         self.assertFalse(notes_response is None)
#         self.assertTrue(len(notes_response.json) == 2)








