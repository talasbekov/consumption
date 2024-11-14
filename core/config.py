from pydantic import BaseSettings, Extra


class Settings(BaseSettings):
    PROJECT_NAME: str
    DESCRIPTION: str
    VERSION: str
    API_V1_PREFIX: str

    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_HOSTNAME: str

    AUTHJWT_SECRET_KEY: str

    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    JWT_ALGORITHM: str

    DEBUG: bool = True
    SENTRY_DSN: str = None

    GENERATE_IP: str = None
    SQLALCHEMY_ECHO: bool = False

    SENTRY_ENABLED: bool = False

    SERVICE_PASSWORD: str

    class Config:
        extra = Extra.allow
        env_file = ".env"


configs = Settings()
