from flask import Flask, request, jsonify, g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sqlite3
import dbDef

app = Flask(__name__)
#make sure to disable this flag 
app.debug = True

@app.before_request
def before_request():
    """This method runs before each request. It will connect to the 
    database and store it in the gloabl variable 'g.db'
    """
    g.db = Session()  #creates session as g.db to add users to

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
    
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == jsonData["userid"]):
        if user != None: 
            #TODO: look up HTTP code
            return "user already exists!", 404

    user = dbDef.User(first_name=jsonData["first_name"],
                    last_name=jsonData["last_name"],
                    userid=jsonData["userid"],
                    groups=(','.join(jsonData["groups"])))
    
    updateGroups(jsonData)
    
    g.db.add(user)
    g.db.commit()
    return jsonify(request.get_json())

@app.route('/users/<userid>', methods=['GET'])
def usersGET(userid):
    """Returns user JSON record if user exist, else returns 404 error if user not found.
    :param userid: userid of requested user record
    :return JSON record of user
    """
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        if user != None:
            return jsonify(user.dictRep())
    return "User <%s> not found." % (userid), 404

@app.route('/users/<userid>', methods=['PUT'])
def usersPUT(userid):
    """Updates user record from input JSON file. Returns 404 error if user not found.
        Also updates group records accordingly. 
    :param userid: userid of user record to be updated
    :return updated JSON record of user 
    """
    jsonData = request.get_json()
    for user in g.db.query(dbDef.User).\
            filter(dbDef.User.userid == userid):
        if user != None:
            updateGroups(jsonData)
            user.updateUser(jsonData)
            g.db.commit()
            return jsonify(user.dictRep())
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
        if user != None:
            userGroups = user.groups.split(",")
            for group in g.db.query(dbDef.Group):
                if group.name in userGroups:
                    group.removeUser(user.userid)
            g.db.delete(user)
            g.db.commit()
            return "User %s deleted." % (userid)
    return "User not found", 404

@app.route('/groups', methods=['POST'])
def groupPost(): #TODO: Should create a EMPTY group w/o JSON... 
    #Creates empty group. POSTs to an existing group should be errors.
    jsonData = request.get_json()
    data = request.get_data()
    print data
    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == jsonData["name"]):
        if group != None: 
            #TODO: look up HTTP code
            return "Group already exists!", 404
    
    #group = dbDef.Group(name=data)
    group = dbDef.Group(name=jsonData["name"], members="") #,
    #               members =(','.join(jsonData["members"])))

    g.db.add(group)
    g.db.commit()
    return jsonify(request.get_json())
    #return data

@app.route('/groups/<group_name>', methods=['PUT'])
def groupPut(group_name):
    """Updates group records. Pushes updated records to users too. 
    :param group_name: Name of group to be updated
    :return :
    """
    jsonData = request.get_json()

    for group in g.db.query(dbDef.Group).\
            filter(dbDef.Group.name == group_name):
        if group != None:
            groupToUsers(jsonData)
            
            #Check if users exist first
            existingUserList = []
            for users in g.db.query(dbDef.User):
                print users
                if users.userid in jsonData["members"]:
                    existingUserList.append(users.userid)
                    print "%s included"%(users.userid)
                else:
                    print "%s not included"%(users.userid)
            print existingUserList
            group.members = (','.join(existingUserList))
            #group.members = (','.join(jsonData["members"])) 
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
    for group in groupQuery.filter(dbDef.Group.name == groupName):
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

def updateGroups(userData):
    userid = str(userData["userid"])
    #1) Groups that don't exist yet == make the group
    #2) send groups to add
    #3) remove from groups which it no longer is in
    userQuery = g.db.query(dbDef.User)
    groupQuery = g.db.query(dbDef.Group)
    newList = userData["groups"]
    oldList = []

    for user in userQuery.filter(dbDef.User.userid == userid):
        if user.groups != None:
            oldList = user.groups.split(",")

    print oldList, newList
    removeList = set(oldList) - set(newList)
    addList = set(newList) - set(oldList)
    print removeList, addList
    groupList = []
    for group in groupQuery:
        if group.name in addList:
            print group.name
            group.addUser(userid)
            print "adding %s to %s" % (userid, group.name)
        
        if group.name in removeList:
            group.removeUser(userid)
            print "removing %s from %s" % (userid, group.name)

        groupList.append(group.name)

    #Creating a new group if it doesn't exist
    for each in addList:
        if each not in groupList:
            print "creating %s" % (each)
            newGroup = dbDef.Group(name=each, members=userid)
            g.db.add(newGroup)
            g.db.commit()

if __name__=='__main__':
    dbDef.init_db() #Will create DB if it doesn't exist
    global engine 
    engine = create_engine('sqlite:////tmp/Planet.db')#, echo=True) 
    global Session 
    Session = sessionmaker(bind=engine)
    app.run()
