from pydantic import BaseModel
from pydantic.alias_generators import to_camel


class PydanticBase(BaseModel):
    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True


class FromCamelCase(BaseModel):
    class Config:
        alias_generator = to_camel


class ToCamelCase(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
