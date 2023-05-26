import copy

from flask import url_for, Blueprint

import flask_restx as restx


class APITest(object):
    def test_root_endpoint(self, app):
        api = restx.Api(app, version="1.0")

        with app.test_request_context():
            url = url_for("root")
            assert url == "/"
            assert api.base_url == "http://localhost/"

    def test_root_endpoint_lazy(self, app):
        api = restx.Api(version="1.0")
        api.init_app(app)

        with app.test_request_context():
            url = url_for("root")
            assert url == "/"
            assert api.base_url == "http://localhost/"

    def test_root_endpoint_with_blueprint(self, app):
        blueprint = Blueprint("api", __name__, url_prefix="/api")
        api = restx.Api(blueprint, version="1.0")
        app.register_blueprint(blueprint)

        with app.test_request_context():
            url = url_for("api.root")
            assert url == "/api/"
            assert api.base_url == "http://localhost/api/"

    def test_root_endpoint_with_blueprint_with_subdomain(self, app):
        blueprint = Blueprint("api", __name__, subdomain="api", url_prefix="/api")
        api = restx.Api(blueprint, version="1.0")
        app.register_blueprint(blueprint)

        with app.test_request_context():
            url = url_for("api.root")
            assert url == "http://api.localhost/api/"
            assert api.base_url == "http://api.localhost/api/"

    def test_root_endpoint_with_nested_blueprint(self, app):
        blueprint = Blueprint("api", __name__, url_prefix="/api")
        blueprint2 = Blueprint("v1", __name__, url_prefix="/v1")
        blueprint.register_blueprint(blueprint2)
        api = restx.Api(blueprint2, version="1.0")
        app.register_blueprint(blueprint)

        with app.test_request_context():
            url = url_for("api.v1.root")
            assert url == "/api/v1/"
            assert api.base_url == "http://localhost/api/v1/"

    def test_root_endpoint_with_nested_blueprint_with_subdomain(self, app):
        blueprint = Blueprint("api", __name__, subdomain="api", url_prefix="/api")
        blueprint2 = Blueprint("v1", __name__, url_prefix="/v1")
        blueprint.register_blueprint(blueprint2)
        api = restx.Api(blueprint2, version="1.0")
        app.register_blueprint(blueprint)

        with app.test_request_context():
            url = url_for("api.v1.root")
            assert url == "http://api.localhost/api/v1/"
            assert api.base_url == "http://api.localhost/api/v1/"

    def test_parser(self):
        api = restx.Api()
        assert isinstance(api.parser(), restx.reqparse.RequestParser)

    def test_doc_decorator(self, app):
        api = restx.Api(app, prefix="/api", version="1.0")
        params = {"q": {"description": "some description"}}

        @api.doc(params=params)
        class TestResource(restx.Resource):
            pass

        assert hasattr(TestResource, "__apidoc__")
        assert TestResource.__apidoc__ == {"params": params}

    def test_doc_with_inheritance(self, app):
        api = restx.Api(app, prefix="/api", version="1.0")
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

    def test_specs_endpoint_not_added(self, app):
        api = restx.Api()
        api.init_app(app, add_specs=False)
        assert "specs" not in api.endpoints
        assert "specs" not in app.view_functions

    def test_specs_endpoint_not_found_if_not_added(self, app, client):
        api = restx.Api()
        api.init_app(app, add_specs=False)
        resp = client.get("/swagger.json")
        assert resp.status_code == 404

    def test_default_endpoint(self, app):
        api = restx.Api(app)

        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("test_resource") == "/test/"

    def test_default_endpoint_lazy(self, app):
        api = restx.Api()

        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        api.init_app(app)

        with app.test_request_context():
            assert url_for("test_resource") == "/test/"

    def test_default_endpoint_with_blueprint(self, app):
        blueprint = Blueprint("api", __name__, url_prefix="/api")
        api = restx.Api(blueprint)
        app.register_blueprint(blueprint)

        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("api.test_resource") == "/api/test/"

    def test_default_endpoint_with_blueprint_with_subdomain(self, app):
        blueprint = Blueprint("api", __name__, subdomain="api", url_prefix="/api")
        api = restx.Api(blueprint)
        app.register_blueprint(blueprint)

        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("api.test_resource") == "http://api.localhost/api/test/"

    def test_default_endpoint_for_namespace(self, app):
        api = restx.Api(app)
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("ns_test_resource") == "/ns/test/"

    def test_default_endpoint_lazy_for_namespace(self, app):
        api = restx.Api()
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        api.init_app(app)

        with app.test_request_context():
            assert url_for("ns_test_resource") == "/ns/test/"

    def test_default_endpoint_for_namespace_with_blueprint(self, app):
        blueprint = Blueprint("api", __name__, url_prefix="/api")
        api = restx.Api(blueprint)
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        app.register_blueprint(blueprint)

        with app.test_request_context():
            assert url_for("api.ns_test_resource") == "/api/ns/test/"

    def test_multiple_default_endpoint(self, app):
        api = restx.Api(app)

        @api.route("/test2/")
        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("test_resource") == "/test/"
            assert url_for("test_resource_2") == "/test2/"

    def test_multiple_default_endpoint_lazy(self, app):
        api = restx.Api()

        @api.route("/test2/")
        @api.route("/test/")
        class TestResource(restx.Resource):
            pass

        api.init_app(app)

        with app.test_request_context():
            assert url_for("test_resource") == "/test/"
            assert url_for("test_resource_2") == "/test2/"

    def test_multiple_default_endpoint_for_namespace(self, app):
        api = restx.Api(app)
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test2/")
        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        with app.test_request_context():
            assert url_for("ns_test_resource") == "/ns/test/"
            assert url_for("ns_test_resource_2") == "/ns/test2/"

    def test_multiple_default_endpoint_lazy_for_namespace(self, app):
        api = restx.Api()
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test2/")
        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        api.init_app(app)

        with app.test_request_context():
            assert url_for("ns_test_resource") == "/ns/test/"
            assert url_for("ns_test_resource_2") == "/ns/test2/"

    def test_multiple_default_endpoint_for_namespace_with_blueprint(self, app):
        blueprint = Blueprint("api", __name__, url_prefix="/api")
        api = restx.Api(blueprint)
        ns = api.namespace("ns", "Test namespace")

        @ns.route("/test2/")
        @ns.route("/test/")
        class TestResource(restx.Resource):
            pass

        app.register_blueprint(blueprint)

        with app.test_request_context():
            assert url_for("api.ns_test_resource") == "/api/ns/test/"
            assert url_for("api.ns_test_resource_2") == "/api/ns/test2/"

    def test_ns_path_prefixes(self, app):
        api = restx.Api()
        ns = restx.Namespace("test_ns", description="Test namespace")

        @ns.route("/test/", endpoint="test_resource")
        class TestResource(restx.Resource):
            pass

        api.add_namespace(ns, "/api_test")
        api.init_app(app)

        with app.test_request_context():
            assert url_for("test_resource") == "/api_test/test/"

    def test_multiple_ns_with_authorizations(self, app):
        api = restx.Api()
        a1 = {"apikey": {"type": "apiKey", "in": "header", "name": "X-API"}}
        a2 = {
            "oauth2": {
                "type": "oauth2",
                "flow": "accessCode",
                "tokenUrl": "https://somewhere.com/token",
                "scopes": {
                    "read": "Grant read-only access",
                    "write": "Grant read-write access",
                },
            }
        }
        ns1 = restx.Namespace("ns1", authorizations=a1)
        ns2 = restx.Namespace("ns2", authorizations=a2)

        @ns1.route("/")
        class Ns1(restx.Resource):
            @ns1.doc(security="apikey")
            def get(self):
                pass

        @ns2.route("/")
        class Ns2(restx.Resource):
            @ns1.doc(security="oauth2")
            def post(self):
                pass

        api.add_namespace(ns1, path="/ns1")
        api.add_namespace(ns2, path="/ns2")
        api.init_app(app)

        assert {"apikey": []} in api.__schema__["paths"]["/ns1/"]["get"]["security"]
        assert {"oauth2": []} in api.__schema__["paths"]["/ns2/"]["post"]["security"]
        unified_auth = copy.copy(a1)
        unified_auth.update(a2)
        assert api.__schema__["securityDefinitions"] == unified_auth

    def test_non_ordered_namespace(self, app):
        api = restx.Api(app)
        ns = api.namespace("ns", "Test namespace")

        assert not ns.ordered

    def test_ordered_namespace(self, app):
        api = restx.Api(app, ordered=True)
        ns = api.namespace("ns", "Test namespace")

        assert ns.ordered

    def test_decorators(self, app, mocker):
        decorator1 = mocker.Mock(return_value=lambda x: x)
        decorator2 = mocker.Mock(return_value=lambda x: x)
        decorator3 = mocker.Mock(return_value=lambda x: x)

        class TestResource(restx.Resource):
            method_decorators = []

        api = restx.Api(decorators=[decorator1])
        ns = api.namespace("test_ns", decorators=[decorator2, decorator3])

        ns.add_resource(TestResource, "/test", endpoint="test")
        api.init_app(app)

        assert decorator1.called is True
        assert decorator2.called is True
        assert decorator3.called is True

    def test_specs_url(self, app):
        api = restx.Api(app)
        specs_url = api.specs_url
        assert specs_url == "/swagger.json"

    def test_url_scheme(self, app):
        api = restx.Api(app, url_scheme="https")
        assert api.specs_url == "https://localhost/swagger.json"
        assert api.base_url == "https://localhost/"
