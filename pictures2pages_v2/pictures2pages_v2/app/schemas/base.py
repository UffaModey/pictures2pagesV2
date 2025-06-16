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

class ImageCreate(ImageBase):
    """
    Attributes required to create a new image.
    Inherits from ImageBase.
    """
    pass

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


# ✍️ Poem schemas for AI-generated poems
class PoemBase(BaseModel):
    """
    Base attributes for poems.
    Used for creating, updating, and displaying poems.
    Feature: Generate and manage AI-generated poems.
    """
    content: str
    is_public: bool = False

class PoemCreate(PoemBase):
    """
    Attributes required to create a new poem.
    Inherits from PoemBase.
    """
    pass

class PoemUpdate(BaseModel):
    """
    Attributes that can be updated for a poem.
    Partial update allowed.
    Feature: Update poem content or visibility.
    """
    content: Optional[str] = None
    is_public: Optional[bool] = None

class PoemResponse(PoemBase):
    """
    Response model for returning a poem to the client.
    Includes additional fields like id, created_at, and owner_id.
    Feature: Display generated poems, browsing, and ownership.
    """
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True


# 📚 Story schemas for AI-generated stories
class StoryBase(BaseModel):
    """
    Base attributes for stories.
    Used for creating, updating, and displaying stories.
    Feature: Generate and manage AI-generated stories.
    """
    content: str
    is_public: bool = False

class StoryCreate(StoryBase):
    """
    Attributes required to create a new story.
    Inherits from StoryBase.
    """
    pass

class StoryUpdate(BaseModel):
    """
    Attributes that can be updated for a story.
    Partial update allowed.
    Feature: Update story content or visibility.
    """
    content: Optional[str] = None
    is_public: Optional[bool] = None

class StoryResponse(StoryBase):
    """
    Response model for returning a story to the client.
    Includes additional fields like id, created_at, and owner_id.
    Feature: Display generated stories, browsing, and ownership.
    """
    id: int
    created_at: datetime
    owner_id: int

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

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    """
    Response model for returning a user's public profile.
    Includes id.
    Feature: Display user profiles, show ownership of content.
    """
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

