import json
import pytest

from flask.json.provider import JSONProvider
from flask_restx import Api, Resource

from datetime import datetime


class CustomJSONTest(object):
    @pytest.mark.parametrize("provider", ["json", "ujson", "sdjson"])
    def test_custom_json(self, app, client, provider):
        provmod = pytest.importorskip(provider)
        class CustomJSONProvider(JSONProvider):
            def dumps(self, obj, **kwargs):
                extra = {"serializer": provmod.__name__}
                return provmod.dumps(
                    obj | extra,
                    default=CustomJSONProvider._default,
                    **kwargs
                )

            def loads(self, s, **kwargs):
                extra = {"deserializer": provmod.__name__}
                return provmod.loads(s, **kwargs) | extra

            @staticmethod
            def _default(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        app.json_provider_class = CustomJSONProvider
        app.json = app.json_provider_class(app)
        api = Api(app)

        @api.route("/test")
        class TestResource(Resource):
            def post(self):
                return api.payload, 200

        resp = client.post("/test", json={"name": "tester"})
        assert resp.status_code == 200
        assert json.loads(resp.data.decode("utf-8"))["serializer"] == provmod.__name__
        assert json.loads(resp.data.decode("utf-8"))["deserializer"] == provmod.__name__
