from pydantic import BaseModel, Field

class PostDefaultInfo(BaseModel):
    text_content: str = Field(min_length=1, max_length=1000, description="Your post can only be from 1 to 1000 characters.")


posts_list_test = [
    {"id": 1, "tag": "dev", "name": "that dev guy", "created_at": "25-07-25", "text_content": "something"},
    {"id": 2, "tag": "anotheruser", "name": "bro", "created_at": "25-04-25", "text_content": "bla-bla"},
    {"id": 3, "tag": "dev", "name": "that dev guy", "created_at": "25-07-25", "text_content": "something again"}
]