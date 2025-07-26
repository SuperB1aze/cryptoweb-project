from fastapi import APIRouter, HTTPException, Depends
from app.schemas.user import UserCreate, SuperUserCreate, UserBio, users_list_test
from datetime import datetime

router_user = APIRouter(prefix="/users", tags=["Users"])

class UserFunctions():
    def user_exist(user_id: int):
        for user in users_list_test:
            if user["id"] == user_id:
                return user
            
        raise HTTPException(status_code = 404, detail="This user does not exist.")


    def user_entry(new_user, role):
        return {
            "id": len(users_list_test) + 1,
            "tag": new_user.tag,
            "name": new_user.name,
            "email": new_user.email,
            "password": new_user.password,
            "age": new_user.age,
            "role": role,
            "creation_date": datetime.now()
        }

@router_user.get("/", summary="get the list of all users")
def userslist():
    return users_list_test

@router_user.get("/{user_id}", summary="check user's profile")
def show_profile(user: dict = Depends(UserFunctions.user_exist)):
    return user

@router_user.post("/create_user", summary="create a user")
def create_user(new_user: UserCreate):
    users_list_test.append(UserFunctions.user_entry(new_user, role="User"))
    return users_list_test

@router_user.post("/create_superuser", summary="create a superuser")
def create_user(new_user: SuperUserCreate):
    users_list_test.append(UserFunctions.user_entry(new_user, role=new_user.role))
    return users_list_test

@router_user.post("/{user_id}/edit", summary="edit user's profile")
def edit_profile(edit_user: UserBio, user: dict = Depends(UserFunctions.user_exist)):
    user["description"] = edit_user.description
    user["city"] = edit_user.city
    user["country"] = edit_user.country
    return user