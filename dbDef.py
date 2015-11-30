from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker #, relationship, backref

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    userid = Column(String)
    #groups 

    def __repr__(self):
        return "<User(First Name='%s', Last Name='%s', userid='%s')>" % (
                    self.first_name, self.last_name, self.userid)

class Group(Base):
	__tablename__ = 'groups'
	id = Column(Integer, primary_key=True)
	name = Column(String) #Name of group
	members = Column(String)	#tied to userid's from User 

	def __repr__(self):
            return "<Group(Name='%s', Members='%s')>" % (
                    self.name, self.members)

def init_db():
    engine = create_engine('sqlite:////tmp/Planet.db')
    Base.metadata.create_all(engine)
