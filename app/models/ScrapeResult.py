from bs4 import BeautifulSoup
from pydantic import BaseModel

class ScrapeResult(BaseModel):
    url: str
    page: BeautifulSoup
    pageRank: int

    class Config:
        arbitrary_types_allowed = True