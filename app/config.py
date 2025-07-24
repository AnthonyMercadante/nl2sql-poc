from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    DATABASE_URL: str = Field("sqlite:///data/demo.db", env="DATABASE_URL")
    MODEL_NAME:   str = Field("defog/sqlcoder-7b-2",     env="MODEL_NAME")
    MAX_TOKENS:   int = 256
    NUM_BEAMS:    int = 4   # recommended by defog

settings = Settings()
