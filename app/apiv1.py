"""APIv1"""
import logging

from fastapi import APIRouter, Depends, Form, Security

from app import config, gpio_utils
from app.dependencies import (
    OAuthForm,
    Token,
    TokenIntrospection,
    authenticate_user,
    get_current_user,
    validate_token,
)
from app.models import ChangeColor, ChangePower, Color, ColorModes

router = APIRouter(tags=["Light Control"])


logger = logging.getLogger(__name__)


@router.post(
    "/token",
    response_model=Token,
    description="Authenticate.",
)
async def login_for_access_token(user_info: OAuthForm = Depends(OAuthForm.form)):
    """Authentication endpoint to obtain token"""
    access_token, role = authenticate_user(user_info)
    return {"access_token": access_token, "token_type": "bearer", "role": role}


@router.post(
    "/token/introspection", response_model=TokenIntrospection, response_model_exclude_none=True
)
async def validate_access_token(token: str = Form(...)):
    """Token introspection endpoint"""
    validate = validate_token(token=token)
    response = await validate
    return response


@router.get("/color", response_model=Color)
async def get_color(user=Security(get_current_user, scopes=["read"])):
    """Return current color and power"""
    color = Color(color=config.current_color(), power=config.current_power())
    logger.info("User %s called get_color", user.username)
    return color


@router.get("/colors", response_model=ColorModes)
async def get_available_colors(user=Security(get_current_user, scopes=["read"])):
    """Return available color settings"""
    logger.info("User %s called get_available_colors", user.username)
    return ColorModes()


@router.put("/reset")
async def reset_lights(user=Security(get_current_user, scopes=["read"])):
    """Reset lights to default"""
    gpio_utils.reset()
    logger.info("User %s called reset_lights", user.username)
    return {}


@router.put("/color", response_model=Color)
async def change_color(color: ChangeColor, user=Security(get_current_user, scopes=["read"])):
    """Change current color or mode"""
    gpio_utils.change_color(color.color)
    logger.info("User %s called change_color with color %s", user.username, color.color)
    return Color(color=config.current_color(), power=config.current_power())


@router.put("/power", response_model=Color)
async def change_power(power: ChangePower, user=Security(get_current_user, scopes=["read"])):
    """Change current power"""
    if power.power:
        gpio_utils.api_turn_on()
    else:
        gpio_utils.api_turn_off()
    logger.info("User %s called change_power with %s", user.username, power.power)
    return Color(color=config.current_color(), power=config.current_power())
