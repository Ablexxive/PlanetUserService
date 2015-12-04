from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    """User class. Contains user records with the following data:
    :param id: unique record id in the DB
    :param first_name: First Name of user
    :param last_name: Last Name of user
    :param userid: User ID of the user
    :param groups: List of groups that the user is a member of
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    userid = Column(String)
    groups = Column(String)

    def __repr__(self):#TODO: add groups to repr
        """Creates string representation of the user
        :return String with all user data
        """
        return "<User(First Name='%s', Last Name='%s', userid='%s', groups='%s')>" % (
                    self.first_name, self.last_name, self.userid, self.groups)
    
    def dictRep(self):
        """Creates dictionary representation of the user that is easily jsonified.
        :return dict with all user data
        """
        groups = self.groups.split(",")
        data = {"first_name":self.first_name, 
                "last_name":self.last_name, "userid":self.userid,
                "groups":self.groups.split(",")}
        return data

    def updateUser(self, jsonData):
        """Updates user record with new data
        :param jsonData: new user record data 
        """
        self.first_name = jsonData["first_name"]
        self.last_name = jsonData["last_name"]
        self.userid = jsonData["userid"]
        self.groups = ",".join(jsonData["groups"])

    def addGroupMembership(self, groupName):
        """Adds new group to groups list.
        :param groupName: name of group to be added
        """
        group = set(self.groups.split(","))
        group.add(groupName)
        self.groups = ",".join(group)

    def removeGroupMembership(self, groupName):
        """Removes group name from groups list.
        :param groupName: name of group to be removed 
        """
        group = set(self.groups.split(","))
        group.remove(groupName)
        self.groups = ",".join(group)

class Group(Base):
    """Group class. Defines table that holds group data.
    :param id: unique id for group
    :param name: name of group
    :param members: string of members in the group, contains valid userids
    """
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    members = Column(String) 

    def __repr__(self):
        """Creates string representation of the group
        :return String with all group data
        """
        return "<Group(Name='%s', Members='%s')>" % (
                    self.name, self.members)

    def dictRep(self):
        """Creates dictionary representation of the group that is easily jsonified.
        :return dict with all group data
        """
        members = []
        if self.members != None:
            members = self.members.split(",")
        data = {"name":self.name, 
                "members":self.members}
        return data

    def addUser(self, userid): #TODO: deal with null set
        """Adds user to group list using userid
        :param userid: userid of user to be added to group members
        """
        if self.members == None:
            self.members = userid
        else:
            members = set(self.members.split(","))
            members.add(userid)
            self.members = ",".join(members)

    def removeUser(self, userid):
        """Removes user from group list 
        :param userid: userid of user to be removed from group members
        """
        members = set(self.members.split(","))
        if userid in members:
            members.remove(userid)
        self.members = ",".join(members)
        
def init_db():
    """Creates database and creates tables based on the classes defined above. Yay ORM!
    """
    engine = create_engine('sqlite:////tmp/Planet.db')
    Base.metadata.create_all(engine)
