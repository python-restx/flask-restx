# checking if sqlalchemy is available
import copy
import flask_restx as restx
from flask import Blueprint
SQLALCHEMY_AVAILABLE = True
try:
    from sqlalchemy import Column
    from sqlalchemy import ForeignKey
    from sqlalchemy import Integer
    from sqlalchemy import String
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import relationship
    from flask_restx.tools import createApiModel
except:
    SQLALCHEMY_AVAILABLE = False


if SQLALCHEMY_AVAILABLE:
    
    Base = declarative_base()
    class Unrelated(Base):
        __tablename__ ='unrelated_table'
        id = Column(Integer, primary_key=True)
        name = Column(String(30))

    class User(Base):
        __tablename__ = "user_account"
        id = Column(Integer, primary_key=True)
        name = Column(String(30))
        fullname = Column(String)
        addresses = relationship(
            "Address", back_populates="user", cascade="all, delete-orphan"
        )
        def __repr__(self):
            return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

    class Address(Base):
        __tablename__ = "address"
        id = Column(Integer, primary_key=True)
        email_address = Column(String, nullable=False)
        user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)
        user = relationship("User", back_populates="addresses")
        def __repr__(self):
            return f"Address(id={self.id!r}, email_address={self.email_address!r})"
    
    class CREATEAPIOMODELTest(object):
        def test_table_withouth_relationships(self, app):
            blueprint = Blueprint("api", __name__, url_prefix="/api")
            api = restx.Api(blueprint, version="1.0")
            app.register_blueprint(blueprint)
            createApiModel(api, User)
