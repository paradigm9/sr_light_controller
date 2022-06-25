"""APIv1"""
from fastapi import APIRouter

from app import config
from app.models import Color, ColorModes

router = APIRouter(tags=["Light Control"])


@router.get("/color", response_model=Color)
async def get_color():
    """Return current color setting"""
    color = Color(color=config.current_color(), power=config.current_power())
    return color


@router.get("/colors", response_model=ColorModes)
async def get_available_colors():
    """Return available color settings"""
    return ColorModes()


@router.put("/color")
async def change_color():
    """Change current color or mode"""
    return
