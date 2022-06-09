# coding:utf-8
__all__= ['createApiModel']

from sqlalchemy.inspection import inspect
from flask_restx import fields
from sqlalchemy import types

_not_allowed = ['TypeEngine', 'TypeDecorator', 'UserDefinedType','PickleType']
conversion = {'INT':'Integer',
    'CHAR': 'String',
    'VARCHAR':'String', 
    'NCHAR': 'String', 
    'NVARCHAR': 'String',
    'TEXT':'String',
    'Text':'String',
    'FLOAT': 'Float',
    'NUMERIC': 'Float',
    'REAL': 'Float',
    'DECIMAL': 'Float',
    'TIMESTAMP': 'DateTime',
    'DATETIME': 'DateTime',
    'CLOB': 'Raw',
    'BLOB': 'Raw',
    'BINARY': 'Raw',
    'VARBINARY': 'Raw',
    'BOOLEAN': 'Boolean',
    'BIGINT': 'Integer',
    'SMALLINT': 'Integer',
    'INTEGER': 'Integer',
    'DATE': 'Date',
    'TIME': 'String',
    'String':'String',
    'Integer':'Integer',
    'SmallInteger':'Integer',
    'BigInteger':'Integer',
    'Numeric':'Float',
    'Float':'Float', 
    'DateTime':'DateTime',
    'Date':'Date',
    'Time':'String',
    'LargeBinary':'Raw',
    'Boolean':'Boolean',
    'Unicode':'String',
    'Concatenable':'String',
    'UnicodeText':'String',
    'Interval':'List',
    'Enum':'List',
    'Indexable':'List',
    'ARRAY':'List',
    'JSON':'List'}

fieldtypes = [r for r in types.__all__ if r not in _not_allowed]

def createApiModel(api, table, modelname='', readonlyfields=[], show=[]):
    """
    api: an instance of API
    table: sqltable
    readonlyfields: optional - fields to be readonly
    show: optiona-  - forcing fields to be a user input
    """
    res = {}
    foreignsmapped = []
    for fieldname, col in table.__table__.columns.items():
        tipo = col.type
        isprimarykey = col.primary_key and fieldname not in show
        params = {}
        fieldnameinreadonly = fieldname in readonlyfields
        if isprimarykey or fieldnameinreadonly:
            params = {'readonly': True}
        if not col.nullable and (not fieldnameinreadonly) and (not isprimarykey):
            params['required'] = True
        if col.default is not None:
            if isinstance(col.default.arg, (str, float, int, bytearray, bytes)):
                params['default'] = col.default.arg
        _tipo = str(tipo).split('(')[0]
        if _tipo in fieldtypes:
            if hasattr(tipo, 'length'):
                params['max_length'] = tipo.length
            if len(col.foreign_keys) > 0:
                foreignsmapped.extend(list(col.foreign_keys))
            res[fieldname] = getattr(fields, conversion[_tipo])(**params)
   # cheking for relationships
    try:
        relationitems = inspect(table).relationships.items()
    except:
        # It could faild in composed primary_keys
        relationitems = []
    for field, relationship in relationitems:
        if relationship.backref != table.__tablename__:
            continue
        try:
            col = list(relationship.local_columns)[0]
            tipo = col.type
            for fieldType in fieldtypes:
                if isinstance(tipo, getattr(types, fieldType)):
                    outparams = {}
                    if hasattr(tipo, 'length'):
                        params['max_length'] = tipo.length
                    if field in readonlyfields:
                        outparams['readonly'] = True
                    if col.foreign_keys is not None:
                        foreignsmapped.extend(list(col.foreign_keys))
                    if relationship.uselist:
                        res[field] = fields.List(
                            getattr(types, fieldType)(**params), **outparams)
                    else:
                        for key, value in outparams.items():
                            params[key] = value
                        res[field] = getattr(fields, fieldType)(**params)
                    break
        except:
            continue
    if modelname in ('', None):
        modelname = table.__tablename__.lower().capitalize()
    return api.model(modelname, res)
