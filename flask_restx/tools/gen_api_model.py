"""Auto generate SQLAlchemy API model schema from database table"""
from flask_restx.fields import (
    List as Listx,
    Nested as Nestedx,
    Raw,
    String,
    DateTime,
    Date,
    Boolean,
    Integer,
    Float,
)

__all__ = ["gen_api_model_from_db"]


SQLALCHEMY_TYPES = {
    "ARRAY": Listx,
    "INT": Integer,
    "CHAR": String,
    "VARCHAR": String,
    "NCHAR": String,
    "NVARCHAR": String,
    "TEXT": String,
    "Text": String,
    "FLOAT": String,
    "NUMERIC": String,
    "REAL": Float,
    "DECIMAL": Float,
    "TIMESTAMP": Float,
    "DATETIME": DateTime,
    "BOOLEAN": Boolean,
    "BIGINT": Integer,
    "SMALLINT": Integer,
    "INTEGER": Integer,
    "DATE": Date,
    "TIME": DateTime,
    "String": String,
    "Integer": Integer,
    "SmallInteger": Integer,
    "BigInteger": Integer,
    "Numeric": Float,
    "Float": Float,
    "DateTime": DateTime,
    "Date": Date,
    "Time": DateTime,
    "Boolean": Boolean,
    "Unicode": String,
    "UnicodeText": String,
    "JSON": Raw,
}


class Utilities:
    """Utilities"""

    def __init__(self, force_camel_case: bool = True):
        self.force_camel_case = force_camel_case

    def to_camel_case(self, attribute_name: str, sep="_"):
        """Convert attribute name separated by sep to camelCase"""
        if not self.force_camel_case:
            return attribute_name
        head, *tail = attribute_name.split(sep)
        tail_capitalized = [k.capitalize() for k in tail]
        return "".join([head] + tail_capitalized)


class ModelSchema(Utilities):
    """Generate API model schema from SQLAlchemy database model"""

    __slots__ = (
        "api",
        "model",
        "fields",
        "ignore_attributes",
        "parents",
    )

    def __init__(
        self,
        api,  # type: any
        model,  # type: any
        fields=[],  # type: list[str]
        force_camel_case=True,  # type: bool
        ignore_attributes=[],  # type: list[str]
        parents=[],  # type: list[any]
    ):
        super().__init__(force_camel_case)
        self.api = api
        self.model = model
        self.fields = fields
        self.ignore_attributes = ignore_attributes
        self.parents = parents

    def get_api_data_type(self, db_field, attribute_name):
        # type: (any, str) -> any
        """Get data type from database field"""
        db_field_cls = SQLALCHEMY_TYPES.get(db_field.type.__class__.__name__, None)
        if db_field_cls is None:
            raise ValueError(
                f"Database field type <{db_field}:{db_field.type}> is not recognized/supported"
            )
        try:
            return db_field_cls(attribute=attribute_name)
        except TypeError:
            return db_field_cls(
                SQLALCHEMY_TYPES.get(
                    db_field.type.__dict__.get("item_type", String).__class__.__name__
                )
            )

    def _foreign_keys_conditon(self, model, elm, with_mapper=False):
        # type: (any, str, bool) -> bool
        has_mapper = hasattr(getattr(model, elm), "mapper")
        base_condition = (
            not elm.startswith("_")
            and not elm.endswith("_")
            and elm not in self.ignore_attributes
            and elm != "Meta"  # Ignore Meta class
            # Should not be a function
            and not callable(getattr(model, elm, None))
        )
        if not with_mapper:
            return base_condition and not has_mapper
        if has_mapper and getattr(model, elm).mapper.class_ in self.parents:
            return False
        return base_condition and has_mapper

    def attrs_without_foreign_keys_condition(self, model, elm):
        # type: (any, str) -> bool
        """Return database model attributes without foreign keys"""
        return self._foreign_keys_conditon(model, elm)

    def attrs_with_foreign_keys_condition(self, model, elm):
        # type: (any, str) -> bool
        """Return database model attributes with only foreign keys"""
        return self._foreign_keys_conditon(model, elm, with_mapper=True)

    def get_model_fields(self, model, fields=[], use_columns=False):
        # type: (any, list[str], bool) -> tuple | list
        """Return model Meta fields or columns fields"""
        if fields:
            return fields
        if hasattr(model, "Meta"):
            if model.Meta.fields == "__all__":
                return model.__dict__
            return model.Meta.fields
        if use_columns:
            return model.__table__.columns.keys()
        return model.__dict__

    def gen_api_model_from_db(self):
        # type: () -> dict
        """Gen API model from DB"""
        self.parents.append(self.model)
        attributes = [
            k
            for k in self.get_model_fields(self.model, self.fields, use_columns=True)
            if self.attrs_without_foreign_keys_condition(self.model, k)
        ]  # type: list[str]

        # For Nested mappings it's recommended to use a proper Meta class for each database model object
        # Like this you can keep track and handle each model fields easly; better than using a default fields
        if not self.fields:
            mappers = [
                k
                for k in self.get_model_fields(self.model)
                if self.attrs_with_foreign_keys_condition(self.model, k)
            ]  # type: list[str | None]
        else:
            mappers = []  # type: list[str | None]
        simple_mappings = {
            self.to_camel_case(attribute): self.get_api_data_type(
                self.model.__dict__.get(attribute), attribute
            )
            for attribute in attributes
        }
        if not self.fields:
            nested = {
                self.to_camel_case(attribute): Listx(
                    Nestedx(
                        self.api.model(
                            f"Nested{attribute.capitalize()}",
                            ModelSchema(
                                api=self.api,
                                model=self.model.__dict__.get(attribute).mapper.class_,
                                force_camel_case=self.force_camel_case,
                                ignore_attributes=self.ignore_attributes,
                                parents=self.parents,
                            ).gen_api_model_from_db(),
                        )
                    )
                )
                for attribute in mappers
            }  # type: dict
        else:
            nested = {}  # type: dict
        return {**simple_mappings, **nested}


def gen_api_model_from_db(
    api, model, fields=[], force_camel_case=True, ignore_attributes=[]
):
    # type: (any, any, list[str], bool, list[str]) -> dict
    """Helper function"""
    return ModelSchema(
        api=api,
        model=model,
        fields=fields,
        force_camel_case=force_camel_case,
        ignore_attributes=ignore_attributes,
        parents=[],  # Need to force the value here otherwise it'll keep track of previous func calls
    ).gen_api_model_from_db()
