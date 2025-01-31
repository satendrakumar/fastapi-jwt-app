from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status, Form, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 6 * 24 * 60

user_name = "johndoe"
user_password = "johndoe"
user_email = "johndoe@example.com"

auth_api_router = APIRouter(prefix=f"/api/auth", tags=["auth"])


class LoginForm:
    def __init__(
            self,
            username: Annotated[
                str,
                Form()
            ],
            password: Annotated[
                str,
                Form()
            ]
    ):
        self.username = username
        self.password = password


class AuthUser(BaseModel):
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def authenticate_user(username: str, password: str):
    if username == user_name and password == user_password:
        return AuthUser(username=username, email=user_email)
    return None


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> AuthUser:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        auth_user = AuthUser(username=username, email=payload.get("email"))
    except InvalidTokenError:
        raise credentials_exception
    return auth_user


@auth_api_router.post("/login")
async def login(form_data: Annotated[LoginForm, Depends()]) -> Token:
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    user_data = {"sub": user.username, "email": user.email}
    access_token = create_access_token(data=user_data, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")
