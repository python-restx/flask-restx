import flask_restx as restx


class PayloadTest(object):
    def assert_errors(self, client, url, data, *errors):
        out = client.post_json(url, data, status=400)
        assert "message" in out
        assert "errors" in out
        for error in errors:
            assert error in out["errors"]

    def test_validation_false_on_constructor(self, app, client):
        api = restx.Api(app, validate=False)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOff(restx.Resource):
            @api.expect(fields)
            def post(self):
                return {}

        data = client.post_json("/validation/", {})
        assert data == {}

    def test_validation_false_on_constructor_with_override(self, app, client):
        api = restx.Api(app, validate=False)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOn(restx.Resource):
            @api.expect(fields, validate=True)
            def post(self):
                return {}

        self.assert_errors(client, "/validation/", {}, "name")

    def test_validation_true_on_constructor(self, app, client):
        api = restx.Api(app, validate=True)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOff(restx.Resource):
            @api.expect(fields)
            def post(self):
                return {}

        self.assert_errors(client, "/validation/", {}, "name")

    def test_validation_true_on_constructor_with_override(self, app, client):
        api = restx.Api(app, validate=True)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOff(restx.Resource):
            @api.expect(fields, validate=False)
            def post(self):
                return {}

        data = client.post_json("/validation/", {})
        assert data == {}

    def _setup_api_format_checker_tests(self, app, format_checker=None):
        class IPAddress(restx.fields.Raw):
            __schema_type__ = "string"
            __schema_format__ = "ipv4"

        api = restx.Api(app, format_checker=format_checker)
        model = api.model("MyModel", {"ip": IPAddress(required=True)})

        @api.route("/format_checker/")
        class TestResource(restx.Resource):
            @api.expect(model, validate=True)
            def post(self):
                return {}

    def test_format_checker_none_on_constructor(self, app, client):
        self._setup_api_format_checker_tests(app)

        out = client.post_json("/format_checker/", {"ip": "192.168.1"})
        assert out == {}

    def test_format_checker_object_on_constructor(self, app, client):
        from jsonschema import FormatChecker

        self._setup_api_format_checker_tests(app, format_checker=FormatChecker())

        out = client.post_json("/format_checker/", {"ip": "192.168.1"}, status=400)
        assert "ipv4" in out["errors"]["ip"]

    def test_validation_false_in_config(self, app, client):
        app.config["RESTX_VALIDATE"] = False
        api = restx.Api(app)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOff(restx.Resource):
            @api.expect(fields)
            def post(self):
                return {}

        out = client.post_json("/validation/", {})

        # assert response.status_code == 200
        # out = json.loads(response.data.decode('utf8'))
        assert out == {}

    def test_validation_in_config(self, app, client):
        app.config["RESTX_VALIDATE"] = True
        api = restx.Api(app)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOn(restx.Resource):
            @api.expect(fields)
            def post(self):
                return {}

        self.assert_errors(client, "/validation/", {}, "name")

    def test_api_payload(self, app, client):
        api = restx.Api(app, validate=True)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class Payload(restx.Resource):
            payload = None

            @api.expect(fields)
            def post(self):
                Payload.payload = api.payload
                return {}

        data = {
            "name": "John Doe",
            "age": 15,
        }

        client.post_json("/validation/", data)

        assert Payload.payload == data

    def test_validation_with_inheritance(self, app, client):
        """It should perform validation with inheritance (allOf/$ref)"""
        api = restx.Api(app, validate=True)

        fields = api.model(
            "Parent",
            {
                "name": restx.fields.String(required=True),
            },
        )

        child_fields = api.inherit(
            "Child",
            fields,
            {
                "age": restx.fields.Integer,
            },
        )

        @api.route("/validation/")
        class Inheritance(restx.Resource):
            @api.expect(child_fields)
            def post(self):
                return {}

        client.post_json(
            "/validation/",
            {
                "name": "John Doe",
                "age": 15,
            },
        )

        self.assert_errors(
            client,
            "/validation/",
            {
                "age": "15",
            },
            "name",
            "age",
        )

    def test_validation_on_list(self, app, client):
        """It should perform validation on lists"""
        api = restx.Api(app, validate=True)

        person = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer(required=True),
            },
        )

        family = api.model(
            "Family",
            {
                "name": restx.fields.String(required=True),
                "members": restx.fields.List(restx.fields.Nested(person)),
            },
        )

        @api.route("/validation/")
        class List(restx.Resource):
            @api.expect(family)
            def post(self):
                return {}

        self.assert_errors(
            client,
            "/validation/",
            {"name": "Doe", "members": [{"name": "Jonn"}, {"age": 42}]},
            "members.0.age",
            "members.1.name",
        )

    def _setup_expect_validation_single_resource_tests(self, app):
        # Setup a minimal Api with endpoint that expects in input payload
        # a single object of a resource
        api = restx.Api(app, validate=True)

        user = api.model("User", {"username": restx.fields.String()})

        @api.route("/validation/")
        class Users(restx.Resource):
            @api.expect(user)
            def post(self):
                return {}

    def _setup_expect_validation_collection_resource_tests(self, app):
        # Setup a minimal Api with endpoint that expects in input payload
        # one or more objects of a resource
        api = restx.Api(app, validate=True)

        user = api.model("User", {"username": restx.fields.String()})

        @api.route("/validation/")
        class Users(restx.Resource):
            @api.expect([user])
            def post(self):
                return {}

    def test_expect_validation_single_resource_success(self, app, client):
        self._setup_expect_validation_single_resource_tests(app)

        # Input payload is a valid JSON object
        out = client.post_json("/validation/", {"username": "alice"})
        assert {} == out

    def test_expect_validation_single_resource_error(self, app, client):
        self._setup_expect_validation_single_resource_tests(app)

        # Input payload is an invalid JSON object
        self.assert_errors(client, "/validation/", {"username": 123}, "username")

        # Input payload is a JSON array (expected JSON object)
        self.assert_errors(client, "/validation/", [{"username": 123}], "")

    def test_expect_validation_collection_resource_success(self, app, client):
        self._setup_expect_validation_collection_resource_tests(app)

        # Input payload is a valid JSON object
        out = client.post_json("/validation/", {"username": "alice"})
        assert {} == out

        # Input payload is a JSON array with valid JSON objects
        out = client.post_json(
            "/validation/", [{"username": "alice"}, {"username": "bob"}]
        )
        assert {} == out

    def test_expect_validation_collection_resource_error(self, app, client):
        self._setup_expect_validation_collection_resource_tests(app)

        # Input payload is an invalid JSON object
        self.assert_errors(client, "/validation/", {"username": 123}, "username")

        # Input payload is a JSON array but with an invalid JSON object
        self.assert_errors(
            client,
            "/validation/",
            [{"username": "alice"}, {"username": 123}],
            "username",
        )

    def test_validation_with_propagate(self, app, client):
        app.config["PROPAGATE_EXCEPTIONS"] = True
        api = restx.Api(app, validate=True)

        fields = api.model(
            "Person",
            {
                "name": restx.fields.String(required=True),
                "age": restx.fields.Integer,
                "birthdate": restx.fields.DateTime,
            },
        )

        @api.route("/validation/")
        class ValidationOff(restx.Resource):
            @api.expect(fields)
            def post(self):
                return {}

        self.assert_errors(client, "/validation/", {}, "name")

    def test_empty_payload(self, app, client):
        api = restx.Api(app, validate=True)

        @api.route("/empty/")
        class Payload(restx.Resource):
            def post(self):

                return {}

        response = client.post(
            "/empty/", data="", headers={"content-type": "application/json"}
        )

        assert response.status_code == 200
