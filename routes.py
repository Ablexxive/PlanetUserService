import logging

from flask import Flask, request, jsonify, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import dbDef

app = Flask(__name__)

@app.before_request
def before_request():
    """This method runs before each request. It will connect to the 
    database and store it in the gloabl variable 'g.db'
    """
    g.db = Session()  #creates session as g.db to add users to
    logging.info("%s", request)
    logging.info("%s", request.data)

@app.teardown_request
def teardown_request(exception):
    """Runs after each request. This closes the g.db session.
    """
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/users', methods=['POST'])
def usersPOST():
    """Creates a new user record using valid user record (JSON).
    POSTs to existing users returns an error. It also CREATES groups that are 
    included in the user record if those groups don't exist vis updateGroup method 
    :return JSON copy of user that is posted successfully 
    """
    jsonData = request.get_json()
    
    if jsonData == None or jsonData.get("userid") == None:
        return "No JSON data  provided or JSON data does not contain <userid> field", 400
    
    userid = jsonData.get("userid")

    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        return "User already exists!", 409

    first_name = jsonData.get("first_name", "")
    last_name = jsonData.get("last_name", "")
    groups = jsonData.get("groups", [])


    user = dbDef.User(first_name=first_name,
                    last_name=last_name,
                    userid=userid,
                    groups=(','.join(groups)))
    
    updateGroups(jsonData)
    
    g.db.add(user)
    g.db.commit()
    return "<%s> added successfully." % (userid)

@app.route('/users/<userid>', methods=['GET'])
def usersGET(userid):
    """Returns user JSON record if user exist, else returns 404 error if user not found.
    :param userid: userid of requested user record
    :return JSON record of user
    """
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        return jsonify(user.dictRep())
    return "User <%s> not found." % (userid), 404

@app.route('/users/<userid>', methods=['PUT'])
def usersPUT(userid):
    """Updates user record from input JSON file. Returns 404 error if user not found.
        Also updates group records accordingly. 
    :param userid: userid of user record to be updated
    :return string indicating successful PUT
    """
    jsonData = request.get_json()
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        updateGroups(jsonData)
        user.updateUser(jsonData)
        g.db.commit()
        return "Data for <%s> updated"%(userid)
    return "User not found", 404

@app.route('/users/<userid>', methods=['DELETE'])
def usersDELETE(userid):
    """Deletes user record based on userid. Returns 404 error if user is not found.
        Also removes user from group list. 
    :param userid: userid of user record to be deleted
    :return conformation message that userid record is deleted
    """
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        userGroups = user.groups.split(",")
        for group in g.db.query(dbDef.Group):
            if group.name in userGroups:
                group.removeUser(user.userid)
        g.db.delete(user)
        g.db.commit()
        return "User %s deleted." % (userid)
    return "User not found", 404

@app.route('/groups', methods=['POST'])
def groupPost(): 
    """Creats empty group. Group name comes from body of request under variable 'name'
    If group already exists, returns error 
    :return name of succesfully created group.
    """
    jsonData = request.get_json()
    
    if jsonData == None or jsonData.get("name") == None:
        return "No JSON data  provided or JSON data does not contain <name> field", 400
    
    groupName = jsonData["name"]

    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == groupName):
        return "Group already exists!", 409
    
    group = dbDef.Group(name=groupName, members="")
    
    g.db.add(group)
    g.db.commit()
    return "Group <%s> successfuly created"%(groupName)

@app.route('/groups/<group_name>', methods=['PUT'])
def groupPut(group_name):
    """Updates group records. Pushes updated records to users too. Returns 404 if group not found.
    :param group_name: Name of group to be updated
    :return Conformation of group update 
    """
    jsonData = request.get_json()

    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        
        groupName = str(jsonData["name"])
        newList = jsonData["members"]
        groupToUsers(groupName, newList)

        existingUserList = []
        # TODO: Filter user list by those in members
        for user in g.db.query(dbDef.User):
            if user.userid in jsonData["members"]:
                existingUserList.append(user.userid)
        group.members = ','.join(existingUserList)
        g.db.commit()
        return "Group %s updated" % (group_name)
    return "Group %s not found!" % (group_name), 404

@app.route('/groups/<group_name>', methods=['GET'])
def groupGet(group_name):
    """Returns group JSON record. Returns 404 if group not found. 
    :param group_name: name of desired group record
    :return JSON record for group_name
    """
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            return jsonify(group.dictRep())
    return "Group %s not found!" % (group_name), 404

@app.route('/groups/<group_name>', methods=['DELETE'])
def groupDelete(group_name):
    """Deletes group record. Returns 404 if group not found.
    :param group_name: name of group to be deleted
    :return: Conformation message that group has been deleted.
    """
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        # TODO: Filter users returned by group list containing group_name
        for user in g.db.query(dbDef.User):
            if user.userid in group.members:
                user.removeGroupMembership(group_name)
        g.db.delete(group)
        g.db.commit()
        return "Group %s deleted!" % (group_name)
    return "Group %s not found!" % (group_name), 404

def groupToUsers(groupName, newList): #groupData):
    """Used to sync up group data and user data of groups.
    :param groupData: JSON data of group listing to be updated
    """
    userQuery = g.db.query(dbDef.User)
    groupQuery = g.db.query(dbDef.Group)
    
    oldList = []

    for group in groupQuery.filter(dbDef.Group.name == groupName):
        if group.members != None:
            oldList = group.members.split(",")
    
    removeList = set(oldList) - set(newList)
    addList = set(newList) - set(oldList)

    for user in userQuery:
        if user.userid in addList:
            user.addGroupMembership(groupName)
        if user.userid in removeList:
            user.removeGroupMembership(groupName)

def updateGroups(userData):
    """Use to sync group data after changing/adding user data. 
    Creates group if group does not exist. 
    :param userData: JSON data of user that is being added/changed
    """
    userQuery = g.db.query(dbDef.User)
    # TODO: Filter the returned list of groups by newList and oldList?
    groupQuery = g.db.query(dbDef.Group)
    
    userid = str(userData["userid"])
    newList = userData["groups"]
    oldList = []

    # TODO: Either search for the single user or add a break in the if condition
    for user in userQuery.filter(dbDef.User.userid == userid):
        if user.groups != None:
            oldList = user.groups.split(",")

    removeList = set(oldList) - set(newList)
    addList = set(newList) - set(oldList)
    
    groupList = []
    for group in groupQuery:
        if group.name in addList:
            group.addUser(userid)
        elif group.name in removeList:
            group.removeUser(userid)
        groupList.append(group.name)

    for each in addList:
        if each not in groupList:
            newGroup = dbDef.Group(name=each, members=userid)
            g.db.add(newGroup)
    g.db.commit()

if __name__=='__main__':
    """Begins flask app and initializes connection to database
    """
    logging.root.setLevel(logging.INFO)
    dbPath = 'sqlite:////tmp/Planet.db'
    engine = dbDef.get_db(dbPath) #Will create DB if it doesn't exist
    
    global Session 
    Session = sessionmaker(bind=engine)
    
    app.debug = True
    app.run()
