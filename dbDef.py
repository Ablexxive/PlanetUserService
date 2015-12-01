from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker #, relationship, backref
import json

Base = declarative_base()

#TODO Comments on the methods :X
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    userid = Column(String)
    groups = Column(String)

    #TODO: groups 

    def __repr__(self):#TODO: add groups to repr
        return "<User(First Name='%s', Last Name='%s', userid='%s')>" % (
                    self.first_name, self.last_name, self.userid)
    
    def dictRep(self):
        #Dictionary representation which can then be jsonified 
        groups = self.groups.split(",")
        data = {"first_name":self.first_name, 
                "last_name":self.last_name, "userid":self.userid,
                "groups":groups}
        return data

    def updateUser(self, jsonData):
        self.first_name = jsonData["first_name"]
        self.last_name = jsonData["last_name"]
        self.userid = jsonData["userid"]

    def addGroupMembership(self, groupName):
        print "adding %s from %s" % (self.userid, groupName)

    def removeGroupMembership(self, groupName):
        print "removing %s from %s "%(self.userid, groupName)
class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String) #Name of group
    members = Column(String)	#tied to userid's from User 

    def __repr__(self):
        return "<Group(Name='%s', Members='%s')>" % (
                    self.name, self.members)

    def dictRep(self):
        #Dictionary representation which can then be jsonified 
        members = []
        if self.members != None:
            members = self.members.split(",")
        data = {"name":self.name, 
                "members":self.members}
        return data

def init_db():
    engine = create_engine('sqlite:////tmp/Planet.db')
    Base.metadata.create_all(engine)