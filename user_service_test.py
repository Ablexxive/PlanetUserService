import json
import os
import tempfile
import unittest

from flask import jsonify
from sqlalchemy.orm import sessionmaker

import dbDef
import user_service

class UserServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, self.dbPath = tempfile.mkstemp()
        engine = dbDef.get_db('sqlite:///'+self.dbPath)
        user_service.Session = sessionmaker(bind=engine)
        user_service.app.config['TESTING'] = True

        self.app = user_service.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.dbPath)

#Helper methods - 
    def createUser(self):
        user = dbDef.User(first_name="john",
                        last_name="smith",
                        userid="jsmith",
                        groups="admin, users")
        session = user_service.Session()
        session.add(user)
        session.commit()
    
    def createGroup(self):
        group = dbDef.Group(name="admin")
        session = user_service.Session()
        session.add(group)
        session.commit()

#Users methods - 
    def test_user_post_fail(self):
        self.createUser()
        userDict = {
                "first_name":"james",
                "last_name":"smith",
                "userid":"jsmith",
                "groups":["newGroup", "users", "other"],
                }
        jsonData = json.dumps(userDict)
        
        rv = self.app.post('/users', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 409)
        
        
    def test_user_post_success(self):
        userDict = {
                "first_name":"alan",
                "last_name":"tester",
                "userid":"atest",
                "groups":["admin", "users", "other"],
                }
        jsonData = json.dumps(userDict)
        rv = self.app.post('/users', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_user_put_fail(self):
        #Attempting to put to a user that does not exist
        userDict = {
                "first_name":"alan",
                "last_name":"tester",
                "userid":"atest",
                "groups":["admin", "users", "other"],
                }
        jsonData = json.dumps(userDict)

        rv = self.app.put('/users/falseUser', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 404)
        
    def test_user_put_success(self):
        self.createUser()
        userDict = {
                "first_name":"james",
                "last_name":"smith",
                "userid":"jsmith",
                "groups":["newGroup", "users", "other"],
                }
        jsonData = json.dumps(userDict)
        
        rv = self.app.put('/users/jsmith', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 200)

    def test_user_get_fail(self):
        rv = self.app.get('/users/falseUser')
        self.assertEqual(rv.status_code, 404)

    def test_user_get_success(self):
        self.createUser()
        rv = self.app.get('/users/jsmith')
        self.assertEqual(rv.status_code, 200)
    
    def test_user_delete_fail(self):
        rv = self.app.delete('/users/falseUser')
        self.assertEqual(rv.status_code, 404)

    def test_user_delete_success(self):
        self.createUser()
        rv = self.app.delete('/users/jsmith')
        self.assertEqual(rv.status_code, 200)

#Group methods
    def test_group_post_fail(self):
        self.createGroup()
        jsonData = json.dumps({
                "name":"admin",
                "members":[],
                })
        
        rv = self.app.post('/groups', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 409)
        
    def test_group_post_success(self):
        jsonData = json.dumps({
                "name":"admin",
                "members":[],
                })
        
        rv = self.app.post('/groups', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        
    def test_group_put_fail(self):
        jsonData = json.dumps({
                "name":"admin",
                "members":[],
                })
        
        rv = self.app.put('/groups/admin', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 404)
        
    def test_group_put_success(self):
        self.createGroup()
        jsonData = json.dumps({
                "name":"admin",
                "members":[],
                })
        
        rv = self.app.put('/groups/admin', data=jsonData,
                            content_type='application/json')
        self.assertEqual(rv.status_code, 200)
    
    def test_group_get_fail(self):
        rv = self.app.get('/groups/falseGroup')
        self.assertEqual(rv.status_code, 404)
   
   def test_group_get_success(self):
        self.createGroup()
        rv = self.app.get('/groups/admin')
        self.assertEqual(rv.status_code, 200)
   
   def test_group_delete_fail(self):
        pass
   
   def test_group_delete_success(self):
        pass

#Tests to see if group list is updated when you delete a user
#tests to see if user data is updated when you delete a group
if __name__ == '__main__':
    unittest.main()
