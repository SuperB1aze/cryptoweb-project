from fastapi import APIRouter, HTTPException, Depends
from app.schemas.post import PostDefaultInfo, posts_list_test
from app.routers.user_routes import UserFunctions
from datetime import datetime

router_post = APIRouter(prefix="/posts", tags=["Posts"])

class PostFunctions():
    @staticmethod
    def post_exist(post_id: int, user: dict = Depends(UserFunctions.user_exist)):
        for post in posts_list_test:
            if post["tag"] == user["tag"] and post["id"] == post_id:
                return posts_list_test[post_id - 1]
            
        raise HTTPException(status_code = 404, detail="This post does not exist.")

@router_post.get("/", summary="get the list of all posts")
def postslist():
    return posts_list_test

@router_post.get("/{user_id}", summary="get the list of all posts made by user")
def user_postlist(user: dict = Depends(UserFunctions.user_exist)):
    user_postlist = []

    for post in posts_list_test:
        if post["tag"] == user["tag"]:
            user_postlist.append({
                "id": post["id"],
                "created_at": post["created_at"],
                "text_content": post["text_content"]
            })
    if user_postlist == []:
        return f"{user["tag"]} hasn't posted anything yet."
    return user_postlist

@router_post.get("/{user_id}/{post_id}", summary="get a specific post made by user")
def user_post(post: dict = Depends(PostFunctions.post_exist)):
    return post
        
@router_post.post("/{user_id}/upload", summary="make a new post")
def new_post(post: PostDefaultInfo, user: dict = Depends(UserFunctions.user_exist)):
    posts_list_test.append({
        "id": len(posts_list_test) + 1,
        "tag": user["tag"],
        "name": user["name"],
        "created_at": datetime.now(),
        "text_content": post.text_content
    })
    return posts_list_test

@router_post.post("/{user_id}/{post_id}/edit", summary="edit a specific post")
def edit_post(edited_content: PostDefaultInfo, post: dict = Depends(PostFunctions.post_exist)):
    post.update({"edited_at": datetime.now(), "text_content": edited_content.text_content})
    return post

@router_post.post("/{user_id}/{post_id}/delete", summary="delete a specific post")
def delete_post(post: dict = Depends(PostFunctions.post_exist)):
    posts_list_test.remove(post)
    return posts_list_test