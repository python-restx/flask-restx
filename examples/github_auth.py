# Example GitHub OAuth application
#
# With the flask-restx project checked out locally, run as follows from the project's root:
# SWAGGER_UI_OAUTH_REDIRECT_URL="xxx" FLASK_APP=examples/github_auth.py FLASK_ENV=development SWAGGER_UI_OAUTH_CLIENT_ID=xxx PYTHONPATH=. flask run
#
# Ensure that SWAGGER_UI_OAUTH_REDIRECT_URL and SWAGGER_UI_OAUTH_CLIENT_ID match your GitHub app's OAuth settings.
#

from flask import Flask
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)

app.config["SWAGGER_UI_OAUTH_REDIRECT_URL"] = os.environ.get("SWAGGER_UI_OAUTH_REDIRECT_URL")
app.config["SWAGGER_UI_OAUTH_CLIENT_ID"] = os.environ.get("SWAGGER_UI_OAUTH_CLIENT_ID")

app.wsgi_app = ProxyFix(app.wsgi_app)

authorizations = {
    'OAuth2': {
        'type': 'oauth2',
        'flow': 'accessCode',
        'authorizationUrl': 'https://github.com/login/oauth/authorize',
        'tokenUrl': '/auth',
        'scopes': {
            'user:email': 'Read user email addresses'
        }
    }
}

api = Api(app, version="1.0", title="Todo API", description="A simple TODO API", authorizations=authorizations)

ns = api.namespace("todos", description="TODO operations")
auth_ns = api.namespace("auth", description="Auth operations")

TODOS = {
    "todo1": {"task": "build an API"},
    "todo2": {"task": "?????"},
    "todo3": {"task": "profit!"},
}

todo = api.model(
    "Todo", {"task": fields.String(required=True, description="The task details")}
)

listed_todo = api.model(
    "ListedTodo",
    {
        "id": fields.String(required=True, description="The todo ID"),
        "todo": fields.Nested(todo, description="The Todo"),
    },
)


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        api.abort(404, "Todo {} doesn't exist".format(todo_id))


parser = api.parser()
parser.add_argument(
    "task", type=str, required=True, help="The task details", location="form"
)


@ns.route("/<string:todo_id>")
@api.doc(responses={404: "Todo not found"}, params={"todo_id": "The Todo ID"})
class Todo(Resource):
    """Show a single todo item and lets you delete them"""

    @api.doc(description="todo_id should be in {0}".format(", ".join(TODOS.keys())))
    @api.marshal_with(todo)
    def get(self, todo_id):
        """Fetch a given resource"""
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    @api.doc(responses={204: "Todo deleted"})
    def delete(self, todo_id):
        """Delete a given resource"""
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return "", 204

    @api.doc(parser=parser)
    @api.marshal_with(todo)
    def put(self, todo_id):
        """Update a given resource"""
        args = parser.parse_args()
        task = {"task": args["task"]}
        TODOS[todo_id] = task
        return task


@ns.route("/")
class TodoList(Resource):
    """Shows a list of all todos, and lets you POST to add new tasks"""

    @api.marshal_list_with(listed_todo)
    def get(self):
        """List all todos"""
        return [{"id": id, "todo": todo} for id, todo in TODOS.items()]

    @api.doc(parser=parser)
    @api.marshal_with(todo, code=201)
    def post(self):
        """Create a todo"""
        args = parser.parse_args()
        todo_id = "todo%d" % (len(TODOS) + 1)
        TODOS[todo_id] = {"task": args["task"]}
        return TODOS[todo_id], 201

@auth_ns.route("/")
class Auth(Resource):
    """Dummy Auth handler"""

    def post(self):
        """Finish auth"""
        return True

if __name__ == "__main__":
    app.run(debug=True)
