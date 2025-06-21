"""
Endpoints for Pictures2Pages app.
Handles user registration, login, image upload, AI story/poem creation, visibility updates, content browsing, and deletion.
"""

import os
import uuid
import boto3
from fastapi import File, UploadFile, HTTPException, Depends, Form, Query
from fastapi.responses import JSONResponse
from typing import Any, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.base import Base
from ..db.session import engine
from .auth import (
    get_db,
    create_access_token,
    get_current_user,
    hash_password,
    authenticate_user,
)
from ..db.models.user import User
from typing import Optional
from ..db.models.image import Image
from ..db.models.contents import GeneratedContent


from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from ..schemas.base import (
    VersionResponse,
    ImageResponse,
    UserCreate,
    GeneratedContentResponse,
    Token,
)
from ..services.generate_content import (
    generate_content_from_image_labels,
    get_caption_for_image,
    extract_s3_filename,
)
from ..version import __version__
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up AWS S3
S3_BUCKET_NAME = "pictures-to-pages-bucket"
S3_REGION = "eu-west-2"  # e.g., us-east-1
AWS_KEY_ID = os.getenv("AWS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=S3_REGION,
)

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
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered"}


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
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


@router.post("/upload-image", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    is_public: bool = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Upload an image to S3 and return its metadata.
    """
    try:

        # Generate a unique file name
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        print(f"Unique file name for uploaded file: {unique_filename}")

        # Upload to S3
        s3_client.upload_fileobj(
            file.file,
            S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={"ContentType": file.content_type},
        )

        # Build the image URL
        image_url = (
            f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{unique_filename}"
        )

        # Save to DB
        image = Image(
            url=image_url,
            description=description,
            is_public=is_public,
            owner_id=current_user.id,
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        return ImageResponse(
            id=image.id,
            url=image.url,
            description=image.description,
            is_public=image.is_public,
            created_at=image.created_at.isoformat(),
            owner_id=image.owner_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")


@router.get("/images", response_model=List[ImageResponse])
def list_user_images(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    images = (
        db.query(Image)
        .filter(Image.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return images


@router.post("/generate-content", response_model=GeneratedContentResponse)
async def generate_content(
    image_url_1: str = Form(...),
    image_url_2: str = Form(...),
    image_url_3: str = Form(...),
    theme: Optional[str] = Form(None),
    is_story: bool = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Generate a story or poem from images, save it, and return it.
    """
    try:
        # 🔍 Extract filenames from image URLs
        key_1 = extract_s3_filename(image_url_1)
        key_2 = extract_s3_filename(image_url_2)
        key_3 = extract_s3_filename(image_url_3)

        # 🧠 Generate captions
        caption_1 = get_caption_for_image(key_1, S3_BUCKET_NAME)
        caption_2 = get_caption_for_image(key_2, S3_BUCKET_NAME)
        caption_3 = get_caption_for_image(key_3, S3_BUCKET_NAME)
        print(f"Key 1: {key_1}")
        print(f"Key 2: {key_2}")
        print(f"Key 3: {key_3}")

        print(f"Caption 1: {caption_1}")
        print(f"Caption 2: {caption_2}")
        print(f"Caption 3: {caption_3}")

        if is_story:
            content_type = "story"
        else:
            content_type = "poem"

        # ✨ Generate content using AI
        result = generate_content_from_image_labels(
            caption_1, caption_2, caption_3, theme=theme, content_type=content_type
        )
        print(f"Generated {content_type} result: {result}")

        # 🗂️ Save to database
        new_content = GeneratedContent(
            image_url_1=image_url_1,
            image_url_2=image_url_2,
            image_url_3=image_url_3,
            caption_1=caption_1,
            caption_2=caption_2,
            caption_3=caption_3,
            title=result["title"],
            content=result[content_type],
            theme=theme,
            is_story=is_story,
            owner_id=current_user.id,
        )
        db.add(new_content)
        db.commit()
        db.refresh(new_content)
        print(f"Generated content saved to DB: {new_content.title}")

        return GeneratedContentResponse.from_orm(new_content)

    except Exception as e:
        print(f"❌ Error generating content: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate content")


@router.patch("/set-visibility", response_model=Any)
async def set_visibility(
    content_id: int = Query(..., description="ID of the content to update"),
    is_public: bool = Query(..., description="New visibility status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Set the visibility of a story or poem (public/private).
    Only the content owner can update visibility.
    Requires authentication.
    """
    content = (
        db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    )

    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    if content.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to modify this content"
        )

    content.is_public = is_public
    db.commit()
    db.refresh(content)

    return {"message": f"Visibility updated for item {content_id} to {is_public}"}


@router.get("/view-content", response_model=List[GeneratedContentResponse])
async def view_content(
    user_id: int = Query(..., description="User ID to filter public content by"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 👈 authentication check
) -> Any:
    """
    View public content (stories or poems) generated by a specific user.
    Only returns content marked as public. Requires authentication.
    """
    content = (
        db.query(GeneratedContent)
        .filter(
            GeneratedContent.owner_id == user_id, GeneratedContent.is_public == True
        )
        .all()
    )
    return content


@router.delete("/delete-content", response_model=Any)
async def delete_content(
    content_id: int = Query(..., description="ID of the content to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete your own content (poem, or story).
    Only the owner of the content can delete it.
    Requires authentication.
    """
    # Fetch content from database
    content = (
        db.query(GeneratedContent).filter(GeneratedContent.id == content_id).first()
    )

    # Handle case where content doesn't exist
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Ensure the authenticated user is the owner
    if content.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this content"
        )

    # Delete the content
    db.delete(content)
    db.commit()

    return {"message": f"Content with ID {content_id} has been deleted successfully"}
