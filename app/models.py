"""Models for API"""
from typing import Dict

from pydantic import BaseModel, Field

from app.config import MODE_MAP


class Color(BaseModel):
    """Model for color"""

    color: str
    power: bool


class ColorModes(BaseModel):
    """Model for available color modes"""

    color_modes: Dict[str, int] = Field(MODE_MAP)
