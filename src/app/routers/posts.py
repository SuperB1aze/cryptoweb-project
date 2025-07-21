from fastapi import APIRouter, HTTPException
from app.schemas.users import UserCreate, SuperUserCreate, UserRead, users_list_test

router_users = APIRouter(prefix="/users", tags=["Users"])

def user_entry(new_user, role):
    return {
        "id": len(users_list_test) + 1,
        "tag": new_user.tag,
        "name": new_user.name,
        "email": new_user.email,
        "password": new_user.password,
        "age": new_user.age,
        "role": role
    }

@router_users.get("/")
def userslist():
    return users_list_test

@router_users.get("/profile/{user_id}", summary="check user's profile")
def show_profile(user_id: int):
    for user in users_list_test:
        if user["id"] == user_id:
            return user
    raise HTTPException(status_code = 404, detail="This user does not exist.")

@router_users.post("/create_user", summary="create a user")
def create_user(new_user: UserCreate):
    users_list_test.append(user_entry(new_user, role="User"))
    return users_list_test

@router_users.post("/create_superuser", summary="create a superuser")
def create_user(new_user: SuperUserCreate):
    users_list_test.append(user_entry(new_user, role=new_user.role))
    return users_list_test

@router_users.post("/profile/{user_id}/edit", summary="edit user's profile")
def edit_profile(edit_user: UserRead, user_id: int):
    for user in users_list_test:
        if user["id"] == user_id:
            user["description"] = edit_user.description
            user["city"] = edit_user.city
            user["country"] = edit_user.country
        return user
    raise HTTPException(status_code = 404, detail="This user does not exist.")