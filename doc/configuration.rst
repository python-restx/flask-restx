Configuration
=============

Flask-RESTX provides the following `Flask configuration values <https://flask.palletsprojects.com/en/1.1.x/config/#configuration-handling>`_:

    Note: Values with no additional description should be covered in more detail
    elsewhere in the documentation. If not, please open an issue on GitHub.

.. py:data:: RESTX_JSON

    Provide global configuration options for JSON serialisation as a :class:`dict`
    of :func:`json.dumps` keyword arguments.

.. py:data:: RESTX_VALIDATE

   Whether to enforce payload validation by default when using the
   ``@api.expect()`` decorator. See the `@api.expect()
   <swagger.html#the-api-expect-decorator>`__ documentation for details.
   This setting defaults to ``False``.

.. py:data:: RESTX_MASK_HEADER

  Choose the name of the *Header* that will contain the masks to apply to your
  answer. See the `Fields masks <mask.html>`__ documentation for details.
  This setting defaults to ``X-Fields``.

.. py:data:: RESTX_MASK_SWAGGER

  Whether to enable the mask documentation in your swagger or not. See the
  `mask usage <mask.html#usage>`__ documentation for details.
  This setting defaults to ``True``.

.. py:data:: RESTX_INCLUDE_ALL_MODELS

  This option allows you to include all defined models in the generated Swagger
  documentation, even if they are not explicitly used in either ``expect`` nor
  ``marshal_with`` decorators.
  This setting defaults to ``False``.

.. py:data:: BUNDLE_ERRORS

  Bundle all the validation errors instead of returning only the first one
  encountered. See the `Error Handling <parsing.html#error-handling>`__ section
  of the documentation for details.
  This setting defaults to ``False``.

.. py:data:: ERROR_404_HELP

.. py:data:: HTTP_BASIC_AUTH_REALM

.. py:data:: SWAGGER_VALIDATOR_URL

.. py:data:: SWAGGER_UI_DOC_EXPANSION

.. py:data:: SWAGGER_UI_OPERATION_ID

.. py:data:: SWAGGER_UI_REQUEST_DURATION

.. py:data:: SWAGGER_UI_OAUTH_APP_NAME

.. py:data:: SWAGGER_UI_OAUTH_CLIENT_ID

.. py:data:: SWAGGER_UI_OAUTH_REALM

.. py:data:: SWAGGER_SUPPORTED_SUBMIT_METHODS
