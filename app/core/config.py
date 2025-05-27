from pydantic import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    database_name: str = "vocational_test"

    class Config:
        env_file = ".env"

settings = Settings()