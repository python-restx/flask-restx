.. _api:

API
===

.. currentmodule:: flask_restx

Core
----

.. autoclass:: Api
    :members:
    :inherited-members:

.. autoclass:: Namespace
    :members:


.. autoclass:: Resource
    :members:
    :inherited-members:


Models
------

.. autoclass:: flask_restx.Model
    :members:

All fields accept a ``required`` boolean and a ``description`` string in ``kwargs``.

.. automodule:: flask_restx.fields
    :members:


Serialization
-------------
.. currentmodule:: flask_restx

.. autofunction:: marshal

.. autofunction:: marshal_with

.. autofunction:: marshal_with_field

.. autoclass:: flask_restx.mask.Mask
    :members:

.. autofunction:: flask_restx.mask.apply


Request parsing
---------------

.. automodule:: flask_restx.reqparse
    :members:

Inputs
~~~~~~

.. automodule:: flask_restx.inputs
    :members:


Errors
------

.. automodule:: flask_restx.errors
    :members:

.. autoexception:: flask_restx.fields.MarshallingError

.. autoexception:: flask_restx.mask.MaskError

.. autoexception:: flask_restx.mask.ParseError


Schemas
-------

.. automodule:: flask_restx.schemas
    :members:


Internals
---------

These are internal classes or helpers.
Most of the time you shouldn't have to deal directly with them.

.. autoclass:: flask_restx.api.SwaggerView

.. autoclass:: flask_restx.swagger.Swagger

.. autoclass:: flask_restx.postman.PostmanCollectionV1

.. automodule:: flask_restx.utils
    :members:
