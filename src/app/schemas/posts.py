from pydantic import BaseModel

class BookInfo(BaseModel):
    name: str
    author: str

books_list = [
    {"id": 1, "name": "быба", "author": "мем"},
    {"id": 2, "name": "биба", "author": "йоба"}
]