"""
Endpoints for Pictures2Pages app.
Handles user registration, login, image upload, AI story/poem creation, visibility updates, content browsing, and deletion.
"""

from typing import Any, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.base import Base
from typing import Annotated
from ..db.session import engine
from .auth import get_db, verify_password, create_access_token, get_current_user, hash_password, authenticate_user
from ..db.models.user import User
from ..db.models.image import Image


from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from ..schemas.base import (VersionResponse,
                            ImageCreate,
                            ImageResponse,
                            PoemCreate,
                            PoemResponse, StoryCreate, StoryResponse,
                            UserCreate, UserResponse, UserLogin, Token)
from ..version import __version__

Base.metadata.create_all(bind=engine)

# Initialize router
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.get("/version", response_model=VersionResponse)
async def get_version() -> Any:
    """Provide version information about the Pictures2Pages web service."""
    return VersionResponse(version=__version__)


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_pw = hash_password(user.password)
    new_user = User(username=user.username,
                    email=user.email,
                    hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered"}

@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/user/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return {"username": current_user.username}

# @router.post("/upload/image")
# def upload_image(current_user: User = Depends(get_current_user)):
#     return {"msg": f"Image uploaded by {current_user.username}"}

@router.post("/upload-image", response_model=ImageResponse)
async def upload_image(image: ImageCreate) -> Any:
    """
    Upload an image.
    Feature: Upload and manage images.
    """
    # Placeholder response with dummy data
    return ImageResponse(
        id=1,
        url=image.url,
        description=image.description,
        is_public=image.is_public,
        created_at="2025-06-01T00:00:00",
        owner_id=1,
    )


@router.post("/create-story", response_model=StoryResponse)
async def create_story(story: StoryCreate) -> Any:
    """
    Generate a story from an image.
    Feature: Generate stories using AI.
    """
    # Placeholder response with dummy data
    return StoryResponse(
        id=1,
        content=story.content,
        is_public=story.is_public,
        created_at="2025-06-01T00:00:00",
        owner_id=1,
    )


@router.post("/create-poem", response_model=PoemResponse)
async def create_poem(poem: PoemCreate) -> Any:
    """
    Generate a poem from an image.
    Feature: Generate poems using AI.
    """
    # Placeholder response with dummy data
    return PoemResponse(
        id=1,
        content=poem.content,
        is_public=poem.is_public,
        created_at="2025-06-01T00:00:00",
        owner_id=1,
    )


@router.patch("/set-visibility", response_model=Any)
async def set_visibility(image_id: int, is_public: bool) -> Any:
    """
    Set visibility of an image, poem, or story.
    Feature: Control content privacy.
    """
    # Placeholder response
    return {"message": f"Visibility updated for item {image_id} to {is_public}"}


@router.get("/view-content", response_model=List[Any])
async def view_content() -> Any:
    """
    View public content (images, poems, stories) by other users.
    Feature: Browse public content.
    """
    # Placeholder response
    return [{"id": 1, "type": "image", "content": "sample content"}]


@router.delete("/delete-content", response_model=Any)
async def delete_content(content_id: int) -> Any:
    """
    Delete your own content (image, poem, or story).
    Feature: Content deletion.
    """
    # Placeholder response
    return {"message": f"Content {content_id} deleted"}
