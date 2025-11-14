import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = True
    DOCS = os.getenv("DOCS_DEV", "docs")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    APPLICATION_ROOT = "/dev"
    ENV = "development"
    DEBUG = True
    PORT = os.getenv("PORT_FLASK")
    DOCS = os.getenv("DOCS_DEV")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")


class ProductionConfig(Config):
    pass


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

flask_env = os.getenv("FLASK_ENV", "development")

if flask_env not in config_by_name:
    raise ValueError(
        f"Invalid value for FLASK_ENV: {flask_env}. "
        f"Must be one of {list(config_by_name.keys())}"
    )
