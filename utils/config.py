from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
  OPENAI_API_KEY: str
  OPENAI_DEFAULT_MODEL: str
  EXA_API_KEY: str

  model_config = {"env_file": ".env"}

#Global singleton instance
settings = Settings()

# Ensure the environment variable is set for libraries that need it
# This is actually a bad design from openai - burying env variables 
# names deep inside their libraries
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
os.environ["OPENAI_DEFAULT_MODEL"] = settings.OPENAI_DEFAULT_MODEL

