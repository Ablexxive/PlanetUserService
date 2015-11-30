from flask import Flask, request, jsonify, g
import sqlite3, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import dbDef
#g = flask.g = Application Global , store DB connection here

app = Flask(__name__)
#make sure to disable this flag 
app.debug = True

@app.before_request
def before_request():
    g.db = Session()  #creates session as g.db to add users to

@app.teardown_request #why exception?
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    
# to return a custom HTTP Code do return "value", <code> :D
@app.route('/users', methods=['POST'])
def postRecord():
    #POST /users
    #Creates a new user record using valid user record (JSON).
    #POSTs to existing users should be treated as errors 
    jsonData = request.get_json()
    
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == jsonData["userid"]):
        if user != None: 
            #TODO: look up HTTP code
            return "user already exists!", 404

    user = dbDef.User(first_name=jsonData["first_name"],
                    last_name=jsonData["last_name"],
                    userid=jsonData["userid"])
    
    g.db.add(user)
    g.db.commit()  #TODO: CURRENTLY GROUPS IS NOT IMPLIMENTED
    return jsonify(request.get_json())

@app.route('/users/<userid>', methods=['GET', 'DELETE', 'PUT'])
def usersLogic(userid):
    data = request.get_data()
    if request.method == 'GET':
        for user in g.db.query(dbDef.User).\
                filter(dbDef.User.userid == userid):
            print user
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
        return group_name
    if request.method == 'DELETE':
        return group_name
    if request.method == 'PUT':
        return group_name

if __name__=='__main__':
    dbDef.init_db() #Will create DB if it doesn't exist
    global engine 
    engine = create_engine('sqlite:////tmp/Planet.db')#, echo=True) 
    global Session 
    Session = sessionmaker(bind=engine)
    app.run()
