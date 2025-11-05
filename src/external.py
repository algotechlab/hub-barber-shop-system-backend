from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from src.core.config import config_by_name, flask_env
from src.db.database import db
from src.resource import all_namespaces


def create_app():
    app = Flask(__name__, static_folder="static")
    config_class = config_by_name[flask_env]
    app.config.from_object(config_class)

    db.init_app(app)

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
    }

    api = Api(
        app,
        prefix=f"/{app.config['APPLICATION_ROOT']}",
        doc=f"/{app.config['DOCS']}",
        authorizations=authorizations,
        security="Bearer Auth",
        version="1.0",
        title="Barber Shop API",
        description="Barber Shop API.",
    )
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(
        app,
        resources={r"/*": {"origins": "*"}, r"/static/*": {"origins": "*"}},
    )

    app.config["JWT_SECRET_KEY"] = "bsconsig"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    @app.route("/")
    def index():
        return "Welcome to Barber Shop API!"

    JWTManager(app)

    # Namespaces registration
    for namespace in all_namespaces():
        api.add_namespace(namespace)
    return app
