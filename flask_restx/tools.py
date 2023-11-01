# coding:utf-8
__all__ = ["createApiModel", "_get_res"]
from sqlalchemy.inspection import inspect
from . import fields
from sqlalchemy import types
from .model import Model

_not_allowed = ["TypeEngine", "TypeDecorator", "UserDefinedType", "PickleType"]
conversion = {
    "INT": "Integer",
    "CHAR": "String",
    "VARCHAR": "String",
    "NCHAR": "String",
    "NVARCHAR": "String",
    "TEXT": "String",
    "Text": "String",
    "FLOAT": "Float",
    "NUMERIC": "Float",
    "REAL": "Float",
    "DECIMAL": "Float",
    "TIMESTAMP": "DateTime",
    "DATETIME": "DateTime",
    "CLOB": "Raw",
    "BLOB": "Raw",
    "BINARY": "Raw",
    "VARBINARY": "Raw",
    "BOOLEAN": "Boolean",
    "BIGINT": "Integer",
    "SMALLINT": "Integer",
    "INTEGER": "Integer",
    "DATE": "Date",
    "TIME": "String",
    "String": "String",
    "Integer": "Integer",
    "SmallInteger": "Integer",
    "BigInteger": "Integer",
    "Numeric": "Float",
    "Float": "Float",
    "DateTime": "DateTime",
    "Date": "Date",
    "Time": "String",
    "LargeBinary": "Raw",
    "Boolean": "Boolean",
    "Unicode": "String",
    "Concatenable": "String",
    "UnicodeText": "String",
    "Interval": "List",
    "Enum": "List",
    "Indexable": "List",
    "ARRAY": "List",
    "JSON": "List",
}

fieldtypes = [r for r in types.__all__ if r not in _not_allowed]


def _get_res(
    table, modelname: str = None, readonlyfields: list = [], show: list = []
) -> Model:
    """Private function to obtain model_columns as a list

    Args:
        table: SQLalchemy Table
        modelname (Optional[str], optional): Custom model name. if it's is None then the modelname will be the capitalized tablename.
        readonlyfields (Optional[list], optional): Set readonly fields. Defaults to [].
        show (Optional[list], optional): Set shown fields. Defaults to [].

    Return:
        Model
    """

    res = {}
    foreignsmapped = []
    # reading from sqlalchemy column into flask-restx column
    for fieldname, col in table.__table__.columns.items():
        tipo = col.type
        isprimarykey = col.primary_key and fieldname not in show
        params = {}
        fieldnameinreadonly = fieldname in readonlyfields
        if isprimarykey or fieldnameinreadonly:
            params = {"readonly": True}
        if not col.nullable and (not fieldnameinreadonly) and (not isprimarykey):
            params["required"] = True
        if col.default is not None:
            if isinstance(col.default.arg, (str, float, int, bytearray, bytes)):
                params["default"] = col.default.arg
        _tipo = str(tipo).split("(")[0]
        if _tipo in fieldtypes:
            if hasattr(tipo, "length"):
                params["max_length"] = tipo.length
            if len(col.foreign_keys) > 0:
                foreignsmapped.extend(list(col.foreign_keys))
            res[fieldname] = getattr(fields, conversion[_tipo])(**params)
    # cheking for relationships
    relationitems = []
    try:
        relationitems = inspect(table).relationships.items()
    except:
        # It could faild in composed primary keys
        pass
    # implementing relationship columns
    for field, relationship in relationitems:
        if relationship.backref != table.__tablename__:
            continue
        try:
            col = list(relationship.local_columns)[0]
            tipo = col.type
            _tipo = str(tipo).split("(")[0]
            if _tipo in fieldtypes:
                outparams = {}
                if hasattr(tipo, "length"):
                    params["max_length"] = tipo.length
                if field in readonlyfields:
                    outparams["readonly"] = True
                if col.foreign_keys is not None:
                    foreignsmapped.extend(list(col.foreign_keys))
                if relationship.uselist:
                    res[field] = fields.List(
                        getattr(fields, conversion[_tipo])(**params), **outparams
                    )
                else:
                    for key, value in outparams.items():
                        params[key] = value
                    res[field] = getattr(fields, conversion[_tipo])(**params)
        except:
            continue
    if modelname in ("", None):
        modelname = table.__tablename__.lower().capitalize()
    return res


def createApiModel(
    api, table, modelname: str = None, readonlyfields: list = [], show: list = []
) -> Model:
    """Create a basic Flask-restx ApiModel by given an sqlachemy Table and a flask-restx api.
    Requires sqlalchemy

    Args:
        api: Flask-restx api
        table: SqlalchemyTable
        modelname (Optional[str], optional): Custom model name. if it's is None then the modelname will be the capitalized tablename.
        readonlyfields (Optional[list], optional): Set readonly fields. Defaults to [].
        show (Optional[list], optional): Set shown fields. Defaults to [].

    Return:
        Model
    """
    res = _get_res(table, modelname, readonlyfields, show)
    return api.model(modelname, res)
