from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    userid = Column(String)
    #groups 

    def __repr__(self):
        return "<User(First Name='%s', Last Name='%s', userid='%s')>" % (
                    self.first_name, self.last_name, self.userid)

