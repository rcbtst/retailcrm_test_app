from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    RETAILCRM_API_KEY: str
    RETAILCRM_SUBDOMAIN: str


settings = Settings()
