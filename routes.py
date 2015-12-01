from flask import Flask, request, jsonify, g
import sqlite3
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

@app.teardown_request #TODO:why exception?
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    
@app.route('/users', methods=['POST'])
def usersPOST():
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

@app.route('/users/<userid>', methods=['GET'])
def usersGET(userid):
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        if user != None:
            #return "test"
            return jsonify(user.dictRep())
    return "User not found", 404

@app.route('/users/<userid>', methods=['PUT'])
def usersPUT(userid):
    jsonData = request.get_json()
    print jsonData
    print type(jsonData)
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        if user != None:
            user.updateUser(jsonData)
            g.db.commit()
            return jsonify(user.dictRep())
            #return "ok"
    return "User not found", 404

@app.route('/users/<userid>', methods=['DELETE'])
def usersDELETE(userid):
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        if user != None:
            g.db.delete(user)
            g.db.commit()
            return "User %s deleted." % (userid)
    return "User not found", 404

@app.route('/groups', methods=['POST'])
def postGroup():
    #Creates empty group. POSTs to an existing group should be errors.
    jsonData = request.get_json()
    
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == jsonData["name"]):
        if group != None: 
            #TODO: look up HTTP code
            return "Group already exists!", 404

    group = dbDef.Group(name=jsonData["name"],
                   members =(','.join(jsonData["members"])))

    g.db.add(group)
    g.db.commit()  #TODO: CURRENTLY GROUPS IS NOT IMPLIMENTED
    return jsonify(request.get_json())

@app.route('/groups/<group_name>', methods=['PUT'])
def groupPut(group_name):
    jsonData = request.get_json()

    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            group.members = (','.join(jsonData["members"]))
            return "Group %s updated" % (group_name)
    return "Group %s not found!" % (group_name), 404

@app.route('/groups/<group_name>', methods=['GET'])
def groupGet(group_name):
    return group_name
@app.route('/groups/<group_name>', methods=['DELETE'])
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
