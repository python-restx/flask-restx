from flask_restx import fields
SQLALCHEMY_AVAILABLE = True
try:
    from sqlalchemy import Column
    from sqlalchemy import ForeignKey
    from sqlalchemy import Integer, String, Float, DateTime,\
        Boolean, Date, JSON
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import relationship
    from flask_restx.tools import _get_res
except:
    SQLALCHEMY_AVAILABLE = False


if SQLALCHEMY_AVAILABLE:

    Base = declarative_base()

    class Unrelated(Base):
        __tablename__ = 'unrelated_table'
        id = Column(Integer, primary_key=True)
        string = Column(String(30))
        float = Column(Float())
        datetime = Column(DateTime())
        boolean = Column(Boolean())
        date = Column(Date())
        json = Column(JSON())

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
        user_id = Column(Integer, ForeignKey(
            "user_account.id"), nullable=False)
        user = relationship("User", back_populates="addresses")

        def __repr__(self):
            return f"Address(id={self.id!r}, email_address={self.email_address!r})"

    def _checkestruct(own, expected):
        for key, value in expected.items():
            try:
                dc1 = own[key].__dict__
                dc2 = value.__dict__
                if not all((dc1.get(k) == v for k, v in dc2.items())):
                    return False
            except KeyError:
                return False
        return True

    class CREATEAPIOMODELTest(object):
        def test_table_without_relationships(self):
            mymodel = {'id': fields.Integer(readonly=True),
                       'string': fields.String(max_length=30),
                       'float': fields.Float(),
                       'boolean': fields.Boolean(),
                       'date': fields.Date(),
                       'json': fields.List()}
            assert _checkestruct(_get_res(Unrelated), mymodel)
        def test_table_with_single_relationship(self):
            # TODO
            assert True

        def test_editable_primary_key(self):
            # TODO
            return True

        def test_making_not_editable_fields(self):
            # TODO
            return True
        