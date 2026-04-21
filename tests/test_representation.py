import pytest

from flask_restx.representations import output_yaml

import flask_restx as restx


class YamlRepresentationsTest(object):

    pexpect = pytest.importorskip("yaml")

    def test_yaml_representation(self, app, client):
        api = restx.Api(app)
        api.representations = {"application/yaml": output_yaml}

        class Foo(restx.Resource):
            def get(self):
                return {"some": {"yaml": ["data", "to", "test"]}}

        api.add_resource(Foo, "/test/")

        res = client.get("/test/", headers={"Accept": "application/yaml"})
        assert res.status_code == 200
        assert res.content_type == "application/yaml"
        assert res.data.decode() == "some:\n  yaml:\n  - data\n  - to\n  - test\n\n"
