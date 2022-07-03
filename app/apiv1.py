"""APIv1"""
from fastapi import APIRouter

from app import config, gpio_utils
from app.models import ChangeColor, ChangePower, Color, ColorModes

router = APIRouter(tags=["Light Control"])


@router.get("/color", response_model=Color)
async def get_color():
    """Return current color and power"""
    color = Color(color=config.current_color(), power=config.current_power())
    return color


@router.get("/colors", response_model=ColorModes)
async def get_available_colors():
    """Return available color settings"""
    return ColorModes()


@router.put("/reset")
async def reset_lights():
    """Reset lights to default"""
    gpio_utils.reset()
    return {}


@router.put("/color", response_model=Color)
async def change_color(color: ChangeColor):
    """Change current color or mode"""
    gpio_utils.change_color(color.color)
    return Color(color=config.current_color(), power=config.current_power())


@router.put("/power", response_model=Color)
async def change_power(power: ChangePower):
    """Change current power"""
    if power.power:
        gpio_utils.api_turn_on()
    else:
        gpio_utils.api_turn_off()
    return Color(color=config.current_color(), power=config.current_power())
