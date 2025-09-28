from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(".env"))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    hf_token: str = Field(alias="HF_TOKEN")
    anthropic_token: str = Field(alias="ANTHROPIC_TOKEN")
    google_apikey: str = Field(alias="GOOGLE_API_KEY")
    openai_apikey: str = Field(alias="OPENAI_API_KEY")


settings = Settings()  # type: ignore
