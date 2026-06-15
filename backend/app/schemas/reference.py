from typing import Annotated

from pydantic import BaseModel, StringConstraints


ReferenceName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=200),
]


class ReferenceCreate(BaseModel):
    name: ReferenceName


class ReferenceUpdate(BaseModel):
    name: ReferenceName


class ReferenceResponse(BaseModel):
    id: str
    name: str
