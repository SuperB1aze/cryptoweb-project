from fastapi import APIRouter, HTTPException
from src.app.schemas.posts import BookInfo, books_list

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("/")
def booklist():
    return books_list

@router.get("/{books_id}", summary="list")
def bookid_check(books_id: int):
    for book in books_list:
        if book["id"] == books_id:
            return book

    raise HTTPException(status_code=404)

@router.post("/new_book", summary="new book")
def create_book(new_book: BookInfo):
    books_list.append({
        "id": len(books_list) + 1,
        "name": new_book.name,
        "author": new_book.author
    })

    return {"success": True}