from typing import List

from pydantic import BaseModel


class ChordItem(BaseModel):
    id: int
    root: str
    quality: str
    inversion: int = 0
    duration: int = 2


class ProgressionRequest(BaseModel):
    chordsData: List[ChordItem]
    model: str
