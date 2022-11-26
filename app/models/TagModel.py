from pydantic import BaseModel

class TagModel(BaseModel):
    tagType: str | None = 'a'
    identifiers: dict[str, str] = {}
