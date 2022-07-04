"""API dependencies"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from pydantic import BaseModel, Field, ValidationError

from app import config

logger = logging.getLogger(__name__)

settings = config.Settings()


class Detail(BaseModel):
    """A simple, message-conveying class."""

    detail: str = Field(..., description="Human-readable message.")


class Token(BaseModel):
    """Response model for auth token"""

    access_token: str
    token_type: str
    role: str


class TokenIntrospection(BaseModel):
    """Response model for Token Introspection Endpoint"""

    active: bool = Field(
        ..., description="If token is currently active, if False, only required field"
    )

    scope: List[str] = Field(None, description="User scopes for endpoints")

    client_id: str = Field(None, description="Future use")

    username: str = Field(None, description="If token is valid, return username")

    exp: int = Field(None, description="Token expiration")


class TokenData(BaseModel):
    """Model to store user token information"""

    username: Optional[str] = None
    scopes: List[str] = []


class OAuthForm(BaseModel):
    """Custom OAuth model and present as form"""

    grant_type: str = "password"
    username: str
    password: str
    scope: str = ""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

    @classmethod
    def form(
        cls,
        username: str = Form(...),
        password: str = Form(...),
    ):
        """method will return form fields"""
        return cls(username=username, password=password)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/token",
    # scopes below are related to the roles/ad groups
    scopes={
        "read": "Permissions to read",
        "user": "Permissions to update limited fields",
        "admin": "Permissions to update all fields",
    },
)


def authenticate_user(user_info: OAuthForm):
    """Authenticate user and generate token

    :param user_info: User credentials
    :type user_info: OAuthForm
    :raises HTTPException: 401 Unauthorized
    :return: jwt
    """
    if user_info.username == settings.username and user_info.password == settings.password:
        logger.info("User %s credentials are valid.", user_info.username)
        expire = datetime.utcnow() + timedelta(minutes=1440)
        # todo: add support for read users later
        permission = ["admin", "read", "user"]
        encoded_jwt = jwt.encode(
            {"sub": user_info.username, "exp": expire, "scopes": permission},
            settings.secret_key,
            algorithm="HS256",
        )
        return encoded_jwt, permission[0]
    logger.warning("User %s credentials appear invalid.", user_info.username)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Username/password verification failed."
    )


async def validate_token(token: str = Depends(oauth2_scheme)):
    """Validate token for token introspection endpoint"""
    token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": "invalid_client",
            "error_description": "The client authentication was invalid",
        },
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms="HS256")
        username: str = payload.get("sub")
        expires = datetime.fromtimestamp(payload.get("exp")).utcnow()
        token_scopes = payload.get("scopes", [])
        if username is None or expires is None or datetime.utcnow() < expires:
            token_introspection = TokenIntrospection(active=False)
        else:
            token_introspection = TokenIntrospection(
                active=True,
                scope=token_scopes,
                client_id="Future use",
                username=username,
                exp=payload.get("exp"),
            )
    except (ExpiredSignatureError, JWTError):
        token_introspection = TokenIntrospection(active=False)
    except ValidationError:
        raise token_exception
    return token_introspection


async def get_current_user(
    security_scopes: SecurityScopes, token: TokenIntrospection = Depends(validate_token)
):
    """Validate token

    :param security_scopes: Endpoint required scopes
    :type security_scopes: SecurityScopes
    :param token: encoded token, defaults to Depends(oauth2_scheme)
    :type token: str, optional
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        token_data = TokenData(username=token.username, scopes=token.scope)
    except (JWTError, ValidationError):
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return token_data
