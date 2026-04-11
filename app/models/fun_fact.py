from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# Enum restricts categories to predefined values.
class Category(str, Enum):
    HOBBIES = "hobbies"
    FOOD = "food"
    TRAVEL = "travel"
    MUSIC = "music"
    SPORTS = "sports"
    TECH = "tech"
    RANDOM = "random"


class FunFactCreate(BaseModel):
    """Request schema for creating a new fun fact."""

    category: Category
    title: str = Field(
        min_length=1,
        max_length=100,
        description="A short, descriptive title for the fun fact",
    )
    fact: str = Field(
        min_length=1,
        max_length=500,
        description="The fun fact content",
    )
    fun_rating: int = Field(
        ge=1,
        le=10,
        description="How fun is this fact on a scale of 1-10",
    )

    # Strip whitespace before length validation.
    @field_validator("title", "fact", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


class FunFactResponse(BaseModel):
    """Response schema with server-managed fields (id, added_at)."""

    id: str
    category: Category
    title: str
    fact: str
    fun_rating: int = Field(ge=1, le=10)
    added_at: datetime
