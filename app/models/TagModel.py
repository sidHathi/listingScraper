from pydantic import BaseModel
import random

class TagModel(BaseModel):
    tagType: str | None = 'a'
    identifiers: dict[str, str] = {}

    def getCssSelector(self) -> str:
        idKey, idVal = random.choice(list(self.identifiers.items()))
        if self.tagType is not None:
            return f'{self.tagType}[{idKey}="{idVal}"]'
        return f'{self.tagType}[{idKey}="{idVal}"]'