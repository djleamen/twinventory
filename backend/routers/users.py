from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.mongo_client import User, get_user, update_user

router = APIRouter(prefix="/users", tags=["users"])


class PreferencesRequest(BaseModel):
    preferences: str


@router.get("/{username}")
def get_user_route(username: str) -> User:
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{username}/preferences")
def update_preferences_route(username: str, request: PreferencesRequest) -> User:
    user = update_user(username, request.preferences)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
