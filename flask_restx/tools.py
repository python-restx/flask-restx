__all__ =  ['createApiModel']

from sqlalchemy.inspection import inspect
from sqlalchemy import types

fieldtypes = types.__all__ #['String', 'Integer', 'Float', 'Boolean', 'DateTime', 'Date',...]

def createApiModel(api, table, modelname='', readonlyfields=[], show=[]):
    """
    api: an instance of API
    table: sqltable
    readonlyfields: optional - fields to be readonly
    show: optiona-  - forcing fields to be showed
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
        for fieldType in fieldtypes:
            if isinstance(tipo, getattr(types, fieldType)):
                if hasattr(tipo, 'length'):
                    params['max_length'] = tipo.length
                if len(col.foreign_keys) > 0:
                    foreignsmapped.extend(list(col.foreign_keys))
                res[fieldname] = getattr(fields, fieldType)(**params)
                break
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
    # TODO
    # -- Check if the model name exists 
    # -- Add support to field description
    return api.model(modelname, res)
