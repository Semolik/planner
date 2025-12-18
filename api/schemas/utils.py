from typing import Annotated

from pydantic import PlainValidator, WithJsonSchema


def empty_str_to_none(value: str | None) -> str | None:
    if value == "":
        return None
    return value


EmptyStrToNone = Annotated[
    str | None,
    PlainValidator(empty_str_to_none),
    WithJsonSchema({"type": "string", "nullable": True}),
]
