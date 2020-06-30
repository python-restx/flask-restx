===========
Flask RESTX
===========

.. image:: https://github.com/python-restx/flask-restx/workflows/Tests/badge.svg?branch=master&event=push
    :target: https://github.com/python-restx/flask-restx/actions?query=workflow%3ATests
    :alt: Tests status
.. image:: https://codecov.io/gh/python-restx/flask-restx/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/python-restx/flask-restx
    :alt: Code coverage
.. image:: https://readthedocs.org/projects/flask-restx/badge/?version=latest
    :target: https://flask-restx.readthedocs.io/en/latest/
    :alt: Documentation status
.. image:: https://img.shields.io/pypi/l/flask-restx.svg
    :target: https://pypi.org/project/flask-restx
    :alt: License
.. image:: https://img.shields.io/pypi/pyversions/flask-restx.svg
    :target: https://pypi.org/project/flask-restx
    :alt: Supported Python versions
.. image:: https://badges.gitter.im/Join%20Chat.svg
    :target: https://gitter.im/python-restx?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
    :alt: Join the chat at https://gitter.im/python-restx
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: black


Flask-RESTX is a community driven fork of `Flask-RESTPlus <https://github.com/noirbizarre/flask-restplus>`_.


Flask-RESTX is an extension for `Flask`_ that adds support for quickly building REST APIs.
Flask-RESTX encourages best practices with minimal setup.
If you are familiar with Flask, Flask-RESTX should be easy to pick up.
It provides a coherent collection of decorators and tools to describe your API
and expose its documentation properly using `Swagger`_.


Compatibility
=============

Flask-RESTX requires Python 2.7 or 3.4+.


Installation
============

You can install Flask-RESTX with pip:

.. code-block:: console

    $ pip install flask-restx

or with easy_install:

.. code-block:: console

    $ easy_install flask-restx


Quick start
===========

With Flask-RESTX, you only import the api instance to route and document your endpoints.

.. code-block:: python

    from flask import Flask
    from flask_restx import Api, Resource, fields

    app = Flask(__name__)
    api = Api(app, version='1.0', title='TodoMVC API',
        description='A simple TodoMVC API',
    )

    ns = api.namespace('todos', description='TODO operations')

    todo = api.model('Todo', {
        'id': fields.Integer(readOnly=True, description='The task unique identifier'),
        'task': fields.String(required=True, description='The task details')
    })


    class TodoDAO(object):
        def __init__(self):
            self.counter = 0
            self.todos = []

        def get(self, id):
            for todo in self.todos:
                if todo['id'] == id:
                    return todo
            api.abort(404, "Todo {} doesn't exist".format(id))

        def create(self, data):
            todo = data
            todo['id'] = self.counter = self.counter + 1
            self.todos.append(todo)
            return todo

        def update(self, id, data):
            todo = self.get(id)
            todo.update(data)
            return todo

        def delete(self, id):
            todo = self.get(id)
            self.todos.remove(todo)


    DAO = TodoDAO()
    DAO.create({'task': 'Build an API'})
    DAO.create({'task': '?????'})
    DAO.create({'task': 'profit!'})


    @ns.route('/')
    class TodoList(Resource):
        '''Shows a list of all todos, and lets you POST to add new tasks'''
        @ns.doc('list_todos')
        @ns.marshal_list_with(todo)
        def get(self):
            '''List all tasks'''
            return DAO.todos

        @ns.doc('create_todo')
        @ns.expect(todo)
        @ns.marshal_with(todo, code=201)
        def post(self):
            '''Create a new task'''
            return DAO.create(api.payload), 201


    @ns.route('/<int:id>')
    @ns.response(404, 'Todo not found')
    @ns.param('id', 'The task identifier')
    class Todo(Resource):
        '''Show a single todo item and lets you delete them'''
        @ns.doc('get_todo')
        @ns.marshal_with(todo)
        def get(self, id):
            '''Fetch a given resource'''
            return DAO.get(id)

        @ns.doc('delete_todo')
        @ns.response(204, 'Todo deleted')
        def delete(self, id):
            '''Delete a task given its identifier'''
            DAO.delete(id)
            return '', 204

        @ns.expect(todo)
        @ns.marshal_with(todo)
        def put(self, id):
            '''Update a task given its identifier'''
            return DAO.update(id, api.payload)


    if __name__ == '__main__':
        app.run(debug=True)


Contributors
============

Flask-RESTX is brought to you by @python-restx. Since early 2019 @SteadBytes,
@a-luna, @j5awry, @ziirish volunteered to help @python-restx keep the project up
and running.
Of course everyone is welcome to contribute and we will be happy to review your
PR's or answer to your issues.


Documentation
=============

The documentation is hosted `on Read the Docs <http://flask-restx.readthedocs.io/en/latest/>`_


.. _Flask: http://flask.pocoo.org/
.. _Swagger: http://swagger.io/


Contribution
============
Want to contribute! That's awesome! Check out `CONTRIBUTING.rst! <https://github.com/python-restx/flask-restx/blob/master/CONTRIBUTING.rst>`_
