import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = True
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    APPLICATION_ROOT = "/dev"
    ENV = "development"
    DEBUG = True
    PORT = os.getenv("DB_PORT")
    DATABASE = os.getenv("DB_NAME")
    USERNAME = os.getenv("DB_USERNAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE}"
    )
    


class ProductionConfig(Config):
    ...

config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}

flask_env = os.getenv("FLASK_ENV", "development")
if flask_env not in config_by_name:
    raise ValueError(f"Invalid value for FLASK_ENV: {flask_env}. Must be one of {list(config_by_name.keys())}")