"""Test Auto generate SQLAlchemy API model"""
import pytest
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

from flask_restx import Resource, fields, marshal
from flask_restx.tools import gen_api_model_from_db


class FixtureTestCase(object):
    @pytest.fixture
    def db(self, app):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        db = SQLAlchemy(app)
        yield db

    @pytest.fixture
    def user_model(self, db):
        class User(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            email = db.Column(db.String(120), unique=True, nullable=False)

            def __repr__(self):
                return "<User %r>" % self.username

            class Meta:
                fields = "__all__"

        return User

    @pytest.fixture
    def user_model_with_relations(self, db):
        class Address(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            road = db.Column(db.String)
            person_id = db.Column(
                db.Integer, db.ForeignKey("person.id"), nullable=False
            )

            def __repr__(self):
                return f"{self.road}"

            class Meta:
                fields = ("road",)

        class Person(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String)
            age = db.Column(db.Integer)
            birth_date = db.Column(db.DateTime)
            addresses = db.relationship("Address", backref="person", lazy=True)

            def __repr__(self):
                return f"{self.name}"

            class Meta:
                fields = ("id", "name", "birth_date", "addresses")

        yield Person

    @pytest.fixture
    def models_with_deep_nested_relations(self, db):
        class Country(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String)
            address = db.relationship("Address", backref="country", lazy=True)

            def __repr__(self):
                return f"{self.name}"

            class Meta:
                fields = "__all__"

        class Address(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            road = db.Column(db.String)
            person_id = db.Column(
                db.Integer, db.ForeignKey("person.id"), nullable=False
            )

            country_id = db.Column(
                db.Integer, db.ForeignKey("country.id"), nullable=False
            )

            def __repr__(self):
                return f"{self.road}"

            class Meta:
                fields = ("id", "road", "country")

        class Person(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            name = db.Column(db.String)
            age = db.Column(db.Integer)
            birth_date = db.Column(db.DateTime)
            addresses = db.relationship("Address", backref="person", lazy=True)

            def __repr__(self):
                return f"{self.name}"

            class Meta:
                fields = ("id", "name", "birth_date", "addresses")

        yield {"person": Person, "address": Address, "country": Country}

    @pytest.fixture
    def declarative_models_with_deep_nested_relations(self):
        Base = declarative_base()

        class Country(Base):
            __tablename__ = "country"

            id = Column(Integer, primary_key=True)
            name = Column(String)
            address = relationship("Address", backref="country", lazy=True)

            def __repr__(self):
                return f"{self.name}"

            class Meta:
                fields = "__all__"

        class Address(Base):
            __tablename__ = "address"

            id = Column(Integer, primary_key=True)
            road = Column(String)
            person_id = Column(Integer, ForeignKey("person.id"), nullable=False)

            country_id = Column(Integer, ForeignKey("country.id"), nullable=False)

            def __repr__(self):
                return f"{self.road}"

            class Meta:
                fields = ("id", "road", "country")

        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            name = Column(String)
            age = Column(Integer)
            birth_date = Column(DateTime)
            addresses = relationship("Address", backref="person", lazy=True)

            def __repr__(self):
                return f"{self.name}"

            class Meta:
                fields = ("id", "name", "birth_date", "addresses")

        yield {"person": Person, "address": Address, "country": Country}


class AutoGenAPIModelTest(FixtureTestCase):
    def test_user_model(self, user_model, api):
        payload = {"id": 1, "username": "toto", "email": "toto@tata.tt"}
        schema = gen_api_model_from_db(api, user_model)
        marshalled = marshal(payload, schema)
        assert marshalled == payload

    def test_model_as_flat_dict_with_marchal_decorator_list(
        self, api, client, user_model
    ):
        fields = api.model("Person", gen_api_model_from_db(api, user_model))

        @api.route("/model-as-dict/")
        class ModelAsDict(Resource):
            @api.marshal_list_with(fields)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert data["definitions"]["Person"] == {
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "email": {"type": "string"},
            },
            "type": "object",
        }

        path = data["paths"]["/model-as-dict/"]
        assert path["get"]["responses"]["200"]["schema"] == {
            "type": "array",
            "items": {"$ref": "#/definitions/Person"},
        }

    def test_model_as_flat_dict_with_marchal_decorator_list_kwargs(
        self, api, client, user_model
    ):
        fields = api.model("Person", gen_api_model_from_db(api, user_model))

        @api.route("/model-as-dict/")
        class ModelAsDict(Resource):
            @api.marshal_list_with(fields, code=201, description="Some details")
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]

        path = data["paths"]["/model-as-dict/"]
        assert path["get"]["responses"] == {
            "201": {
                "description": "Some details",
                "schema": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Person"},
                },
            }
        }

    def test_model_as_dict_with_list(self, api, client, db):
        class User(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String(80), unique=True, nullable=False)
            tags = db.Column(db.ARRAY(db.String))

            def __repr__(self):
                return "<User %r>" % self.username

            class Meta:
                fields = "__all__"

        fields = api.model("Person", gen_api_model_from_db(api, User))

        @api.route("/model-with-list/")
        class ModelAsDict(Resource):
            @api.doc(model=fields)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert data["definitions"]["Person"] == {
            "properties": {
                "id": {"type": "integer"},
                "username": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "type": "object",
        }

        path = data["paths"]["/model-with-list/"]
        assert path["get"]["responses"]["200"]["schema"] == {
            "$ref": "#/definitions/Person"
        }

    def test_model_as_nested_dict_with_list(
        self, api, client, user_model_with_relations
    ):

        person = api.model(
            "Person", gen_api_model_from_db(api, user_model_with_relations)
        )

        @api.route("/model-with-list/")
        class ModelAsDict(Resource):
            @api.doc(model=person)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert "NestedAddresses" in data["definitions"]

    def test_model_as_nested_dict_with_list_limited_fields(
        self, api, client, user_model_with_relations
    ):

        person = api.model(
            "Person", gen_api_model_from_db(api, user_model_with_relations)
        )

        @api.route("/model-with-list/")
        class ModelAsDict(Resource):
            @api.doc(model=person)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert "NestedAddresses" in data["definitions"]
        assert data["definitions"]["Person"] == {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "birthDate": {"format": "date-time", "type": "string"},
                "addresses": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/NestedAddresses"},
                },
            },
            "type": "object",
        }
        assert data["definitions"]["NestedAddresses"] == {
            "properties": {"road": {"type": "string"}},
            "type": "object",
        }
        path = data["paths"]["/model-with-list/"]
        assert path["get"]["responses"]["200"]["schema"] == {
            "$ref": "#/definitions/Person"
        }

    def test_model_as_deep_nested_dict_with_list_limited_fields(
        self, api, client, models_with_deep_nested_relations
    ):

        person = api.model(
            "Person",
            gen_api_model_from_db(api, models_with_deep_nested_relations["person"]),
        )

        @api.route("/model-with-list/")
        class ModelAsDict(Resource):
            @api.doc(model=person)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert "NestedAddresses" in data["definitions"]
        assert "NestedCountry" in data["definitions"]
        assert data["definitions"]["Person"] == {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "birthDate": {"format": "date-time", "type": "string"},
                "addresses": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/NestedAddresses"},
                },
            },
            "type": "object",
        }
        assert data["definitions"]["NestedAddresses"] == {
            "properties": {
                "id": {"type": "integer"},
                "road": {"type": "string"},
                "country": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/NestedCountry"},
                },
            },
            "type": "object",
        }
        assert data["definitions"]["NestedCountry"] == {
            "properties": {"id": {"type": "integer"}, "name": {"type": "string"}},
            "type": "object",
        }
        path = data["paths"]["/model-with-list/"]
        assert path["get"]["responses"]["200"]["schema"] == {
            "$ref": "#/definitions/Person"
        }

    def test_model_as_deep_nested_dict_with_list_static_fields(
        self, api, client, models_with_deep_nested_relations
    ):

        addresses = api.model(
            "Addresses",
            gen_api_model_from_db(
                api, models_with_deep_nested_relations["address"], fields=("id", "road")
            ),
        )
        countries = api.model(
            "Countries",
            gen_api_model_from_db(
                api, models_with_deep_nested_relations["country"], fields=("name",)
            ),
        )
        person = api.model(
            "Person",
            {
                **gen_api_model_from_db(
                    api,
                    models_with_deep_nested_relations["person"],
                    fields=("id", "name", "birth_date"),
                ),
                "customAddressesFieldName": fields.List(fields.Nested(addresses)),
                "customCountriesFieldName": fields.List(fields.Nested(countries)),
            },
        )

        @api.route("/model-with-list/")
        class ModelAsDict(Resource):
            @api.doc(model=person)
            def get(self):
                return {}

        data = client.get_specs()

        assert "definitions" in data
        assert "Person" in data["definitions"]
        assert "Addresses" in data["definitions"]
        assert "Countries" in data["definitions"]
        assert data["definitions"]["Person"] == {
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "birthDate": {"format": "date-time", "type": "string"},
                "customAddressesFieldName": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Addresses"},
                },
                "customCountriesFieldName": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Countries"},
                },
            },
            "type": "object",
        }
        assert data["definitions"]["Addresses"] == {
            "properties": {"id": {"type": "integer"}, "road": {"type": "string"}},
            "type": "object",
        }
        assert data["definitions"]["Countries"] == {
            "properties": {"name": {"type": "string"}},
            "type": "object",
        }
        path = data["paths"]["/model-with-list/"]
        assert path["get"]["responses"]["200"]["schema"] == {
            "$ref": "#/definitions/Person"
        }

    def test_declarative_model_as_deep_nested_dict_with_list_limited_fields(
        self, api, client, declarative_models_with_deep_nested_relations
    ):
        return self.test_model_as_deep_nested_dict_with_list_limited_fields(
            api, client, declarative_models_with_deep_nested_relations
        )

    def test_declarative_model_as_deep_nested_dict_with_list_static_fields(
        self, api, client, declarative_models_with_deep_nested_relations
    ):
        return self.test_model_as_deep_nested_dict_with_list_static_fields(
            api, client, declarative_models_with_deep_nested_relations
        )
