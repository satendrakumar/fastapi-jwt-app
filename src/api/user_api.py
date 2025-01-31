from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.api.auth_api import AuthUser, get_current_user

user_api_router = APIRouter(prefix=f"/api/users", tags=["auth"])


class UserData(BaseModel):
    username: str
    email: str


@user_api_router.get("/list")
async def get_user_list(current_user: Annotated[AuthUser, Depends(get_current_user)]):
    return [{"email": current_user.email, "username": current_user.username}]


@user_api_router.post("/create")
async def create_user(user_data: UserData, current_user: Annotated[AuthUser, Depends(get_current_user)]):
    print("current_user", current_user)
    print("user_data", user_data)
    return user_data
