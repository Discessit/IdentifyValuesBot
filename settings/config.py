from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    OPENAI_API_KEY: SecretStr
    ASSISTANT_DEFAULT_API_KEY: SecretStr
    DATABASE_URL: SecretStr
    ASSISTANT_VALUES_API_KEY: SecretStr
    ASSISTANT_SAVE_VALUES_API_KEY: SecretStr

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()

