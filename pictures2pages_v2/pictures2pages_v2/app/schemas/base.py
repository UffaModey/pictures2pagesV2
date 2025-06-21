"""Define response model for the endpoint version."""

from pydantic import BaseModel, Field, EmailStr  # type: ignore
from typing import Optional
from datetime import datetime


# 🎯 Version endpoint
class VersionResponse(BaseModel):
    """
    Response model for the /version endpoint.
    Shows the current version of the Pictures2Pages API.
    Feature: API health check / version reporting.
    """

    version: str = Field(..., example="1.0.0")


# 🖼️ Image schemas for managing image uploads
class ImageBase(BaseModel):
    """
    Base attributes for images.
    Used when creating, updating, and displaying images.
    Feature: Upload and manage images.
    """

    url: str
    description: Optional[str] = None
    is_public: bool = False


class ImageResponse(ImageBase):
    """
    Response model for returning an image to the client.
    Includes additional fields like id, created_at, and owner_id.
    Feature: Return uploaded images, browsing, and ownership.
    """

    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True


class GeneratedContentResponse(BaseModel):
    """
    Response model for returning a story or poem to the client.
    Used for creating, updating, and displaying poems or stories.
    Feature: Generate and manage AI-generated poems and stories.
    """

    id: int
    created_at: datetime
    owner_id: int
    content: str
    theme: str
    is_public: bool = False
    image_url_1: str
    image_url_2: str
    image_url_3: str
    caption_1: str
    caption_2: str
    caption_3: str

    class Config:
        orm_mode = True


# 👤 User schemas for registration and profile responses
class UserBase(BaseModel):
    """
    Base attributes for users.
    Includes username and email (no password).
    Feature: User profile information.
    """

    username: str
    email: str


class UserCreate(UserBase):
    """
    Attributes required to create a new user.
    Includes password field for registration.
    Feature: User registration with AWS Cognito.
    """

    username: str
    email: EmailStr  # This will reject None!
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
