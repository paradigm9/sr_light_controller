"""Entry for the API to interact with GPIO Pins"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import apiv1

tags = [{"name": "Light Control", "description": "Endpoints for controlling SR Lights"}]

app = FastAPI(
    title="SR Lights API",
    version="1.0",
    description="API to interact with SR Lights",
    openapi_tags=tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http(s?):\/\/.*\.pycontroller\.net",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(apiv1.router, prefix="/api/v1")

if __name__ == "__main__":
    # for testing only
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8585,
        log_level="debug",
        log_config="loggingconfig.yml",
    )
