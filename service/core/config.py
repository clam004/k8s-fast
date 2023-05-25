from starlette.datastructures import CommaSeparatedStrings
from pydantic import BaseSettings
from functools import lru_cache
import os

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
API_V1_STR = "/api/v1"
PROJECT_NAME = "K8s-fastAPI"

class Settings(BaseSettings):
    API_KEY: str
    class Config:
        env_file = '.env'

@lru_cache()
def get_settings():
    return Settings()