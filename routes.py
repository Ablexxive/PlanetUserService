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
                    userid=jsonData["userid"],
                    groups=(','.join(jsonData["groups"])))
    
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
def groupPost(): #TODO: Should create a EMPTY group w/o JSON... 
    #Creates empty group. POSTs to an existing group should be errors.
    jsonData = request.get_json()
    #data = request.get_data()
    #print data
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == jsonData["name"]):
        if group != None: 
            #TODO: look up HTTP code
            return "Group already exists!", 404
    
    #group = dbDef.Group(name=data)
    group = dbDef.Group(name=jsonData["name"]) #,
    #               members =(','.join(jsonData["members"])))

    g.db.add(group)
    g.db.commit()  #TODO: CURRENTLY GROUPS IS NOT IMPLIMENTED
    return jsonify(request.get_json())
    #return data

@app.route('/groups/<group_name>', methods=['PUT'])
def groupPut(group_name):
    jsonData = request.get_json()

    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            groupToUsers(jsonData)
            group.members = (','.join(jsonData["members"]))
            g.db.commit() #Commit AFTER calling groupToUsers, to keep old/new lists in memory 
            return "Group %s updated" % (group_name)
    return "Group %s not found!" % (group_name), 404

@app.route('/groups/<group_name>', methods=['GET'])
def groupGet(group_name):
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            return jsonify(group.dictRep())
    return "Group %s not found!" % (group_name), 404

@app.route('/groups/<group_name>', methods=['DELETE'])
def groupDelete(group_name):
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            g.db.delete(group)
            g.db.commit()
            return "Group %s deleted!" % (group_name)
    return "Group %s not found!" % (group_name), 404

#Group member list managment methods
#Call when you add a group
#Should send appending lists to User's to add
def groupToUsers(groupData):
    groupName = str(groupData["name"])
    print type(groupName)
    newList = groupData["members"]
    #1) send groupName to member to add to list
    #2) compare against old list to remove group from those members
    
    userQuery = g.db.query(dbDef.User)
    groupQuery = g.db.query(dbDef.Group)
    oldList = []
    for group in groupQuery.filter(dbDef.Group.name == 'Admin'):
        if group.members != None:
            oldList = group.members.split(",")
    
    print oldList, newList
    print list(set(oldList) - set(newList))  # to be deleted
    print list(set(newList) - set(oldList))  # to be added 
    removeList = set(oldList) - set(newList)
    addList = set(newList) - set(oldList)

    for user in userQuery: #.filter(dbDef.User.userid):
        if user.userid in addList:
            print "adding %s "%(user.userid)
            user.addGroupMembership(groupName)
        if user.userid in removeList:
            print "deleting %s "%(user.userid)
            user.removeGroupMembership(groupName)

if __name__=='__main__':
    dbDef.init_db() #Will create DB if it doesn't exist
    global engine 
    engine = create_engine('sqlite:////tmp/Planet.db')#, echo=True) 
    global Session 
    Session = sessionmaker(bind=engine)
    app.run()
