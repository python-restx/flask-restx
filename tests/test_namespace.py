# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from http import HTTPStatus
import re
from six import iteritems

import flask_restx as restx

from flask_restx import Namespace, Model, OrderedModel, fields


class NamespaceTest(object):
    def test_parser(self):
        api = Namespace("test")
        assert isinstance(api.parser(), restx.reqparse.RequestParser)

    def test_doc_decorator(self):
        api = Namespace("test")
        params = {"q": {"description": "some description"}}

        @api.doc(params=params)
        class TestResource(restx.Resource):
            pass

        assert hasattr(TestResource, "__apidoc__")
        assert TestResource.__apidoc__ == {"params": params}

    def test_doc_with_responses(self):
        api = Namespace("test")

        person = api.model("Person", {
            "name": fields.String(description="Name of person")
        })
        
        @api.route("int_response/")
        class IntResponseCodeResource(restx.Resource):
            @api.doc("get_int_response")
            @api.marshal_with(person, code=200)
            def get(self, **kwargs):
                """Get name of person"""
                return {}, 200

            @api.response(200, "Doing great")
            def post(self, **kwargs):
                return {}, 200

        @api.route("str_response/")
        class StrResponseCodeResource(restx.Resource):
            @api.doc("get_str_response")
            @api.marshal_with(person, code='200')
            def get(self, **kwargs):
                """Get name of person"""
                return {}, '200'

            @api.response('200', "Doing great")
            def post(self, **kwargs):
                return {}, '200'

        @api.route("enum_response/")
        class EnumResponseCodeResource(restx.Resource):
            @api.doc("get_enum_response")
            @api.marshal_with(person, code=HTTPStatus.OK)
            def get(self, **kwargs):
                """Get name of person"""
                return {}, HTTPStatus.OK
                
            @api.response(HTTPStatus.OK, "Doing great")
            def post(self, **kwargs):
                return {}, HTTPStatus.OK

        @api.route("default_response/")
        class DefaultResponseCodeResource(restx.Resource):
            @api.doc("get_int_response")
            @api.marshal_with(person, code='default')
            def get(self, **kwargs):
                """Get name of person"""
                return {}, 200

            @api.response('default', "Doing great")
            def post(self, **kwargs):
                return {}, 200
        
        # Extract first response code from apidoc, for each of the three get functions defined above
        response_code_dict = {
            resource_class.__name__:
                {"get": [
                    code for code in resource_class.get.__apidoc__["responses"]
                ][0],
                "post":
                [
                    code for code in resource_class.post.__apidoc__["responses"]
                ][0],}
            for resource_class in [IntResponseCodeResource, StrResponseCodeResource, EnumResponseCodeResource, DefaultResponseCodeResource]
        }
        
        for response_name, response_method_dict in iteritems(response_code_dict):
            for method_name, response_code in iteritems(response_method_dict):
                assert response_code in ['200', 'default'], f"{response_name}.{method_name} does not return the correct status code"

    def test_doc_with_inheritance(self):
        api = Namespace("test")
        base_params = {
            "q": {
                "description": "some description",
                "type": "string",
                "paramType": "query",
            }
        }
        child_params = {
            "q": {"description": "some new description"},
            "other": {"description": "another param"},
        }

        @api.doc(params=base_params)
        class BaseResource(restx.Resource):
            pass

        @api.doc(params=child_params)
        class TestResource(BaseResource):
            pass

        assert TestResource.__apidoc__ == {
            "params": {
                "q": {
                    "description": "some new description",
                    "type": "string",
                    "paramType": "query",
                },
                "other": {"description": "another param"},
            }
        }

    def test_model(self):
        api = Namespace("test")
        api.model("Person", {})
        assert "Person" in api.models
        assert isinstance(api.models["Person"], Model)

    def test_ordered_model(self):
        api = Namespace("test", ordered=True)
        api.model("Person", {})
        assert "Person" in api.models
        assert isinstance(api.models["Person"], OrderedModel)

    def test_schema_model(self):
        api = Namespace("test")
        api.schema_model("Person", {})
        assert "Person" in api.models

    def test_clone(self):
        api = Namespace("test")
        parent = api.model("Parent", {})
        api.clone("Child", parent, {})

        assert "Child" in api.models
        assert "Parent" in api.models

    def test_clone_with_multiple_parents(self):
        api = Namespace("test")
        grand_parent = api.model("GrandParent", {})
        parent = api.model("Parent", {})
        api.clone("Child", grand_parent, parent, {})

        assert "Child" in api.models
        assert "Parent" in api.models
        assert "GrandParent" in api.models

    def test_inherit(self):
        authorizations = {
            "apikey": {"type": "apiKey", "in": "header", "name": "X-API-KEY"}
        }
        api = Namespace("test", authorizations=authorizations)
        parent = api.model("Parent", {})
        api.inherit("Child", parent, {})

        assert "Parent" in api.models
        assert "Child" in api.models
        assert api.authorizations == authorizations

    def test_inherit_from_multiple_parents(self):
        api = Namespace("test")
        grand_parent = api.model("GrandParent", {})
        parent = api.model("Parent", {})
        api.inherit("Child", grand_parent, parent, {})

        assert "GrandParent" in api.models
        assert "Parent" in api.models
        assert "Child" in api.models

    def test_api_payload(self, app, client):
        api = restx.Api(app, validate=True)
        ns = restx.Namespace("apples")
        api.add_namespace(ns)

        fields = ns.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @ns.route("/validation/")
        class Payload(restx.Resource):
            payload = None

            @ns.expect(fields)
            def post(self):
                Payload.payload = ns.payload
                return {}

        data = {
            "name": "John Doe",
            "age": 15,
        }

        client.post_json("/apples/validation/", data)

        assert Payload.payload == data

    def test_api_payload_strict_verification(self, app, client):
        api = restx.Api(app, validate=True)
        ns = restx.Namespace("apples")
        api.add_namespace(ns)

        fields = ns.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
            strict=True,
        )

        @ns.route("/validation/")
        class Payload(restx.Resource):
            payload = None

            @ns.expect(fields)
            def post(self):
                Payload.payload = ns.payload
                return {}

        data = {
            "name": "John Doe",
            "agge": 15,  # typo
        }

        resp = client.post_json("/apples/validation/", data, status=400)
        assert re.match("Additional properties are not allowed \(u*'agge' was unexpected\)", resp["errors"][""])
