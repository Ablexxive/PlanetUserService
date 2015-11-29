from flask import Flask, request, jsonify, g
import sqlite3, json
from sqlalchemy import create_engine
import dbDefinition
#g = flask.g = Application Global , store DB connection here

app = Flask(__name__)
#make sure to disable this flag 
app.debug = True

# to return a custom HTTP Code do return "value", <code> :D
@app.route('/users', methods=['POST'])
def postRecord():
    #POST /users
    #Creates a new user record using valid user record (JSON).
    #POSTs to existing users should be treated as errors
    
    print request.get_json()
    print request.headers
    return jsonify(request.get_json())

@app.route('/users/<userid>', methods=['GET', 'DELETE', 'PUT'])
def usersLogic(userid):
    data = request.get_data()
    if request.method == 'GET':
        return userid 
    if request.method == 'DELETE':
        return userid
    if request.method == 'PUT':
        return userid
    
@app.route('/groups', methods=['POST'])
def postGroup():
    #Creates empty group. POSTs to an existing group should be errors.
    data = request.get_data()
    return data

@app.route('/groups/<group_name>', methods=['GET', 'DELETE', 'PUT'])
def groupLogic(group_name):
    data = request.get_data()
    if request.method == 'GET':
        return userid 
    if request.method == 'DELETE':
        return userid
    if request.method == 'PUT':
        return userid

if __name__=='__main__':
    dbDefinition.init_db() #Will create DB if it doesn't exist
    app.run()
"""
#Use app.route('/', methods=DESIRED) for splitting methods
@app.route('/', methods=['PUT', 'POST'])
def hello_world():
    if request.method == 'POST' or request.method == 'PUT':
        data = request.get_data()
        print data
        print type(data)
        return data
    else:
        return 'Hello World \n'
"""
