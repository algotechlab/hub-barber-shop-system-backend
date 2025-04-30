from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api

from src.db.database import db
from src.resource.user import user_us
from src.resource.login import login_ns
from src.settings._base import config_by_name, flask_env


def create_app():
    app = Flask(__name__, static_folder="static")
    config_class = config_by_name[flask_env]
    app.config.from_object(config_class)
    
    db.init_app(app) # init database
    
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
        doc=f"/{app.config["DOCS"]}",
        authorizations=authorizations,
        security="Bearer Auth",
        version="1.0",
        title="Barbearia DG",
        description="Backend Barbearia DG.",
    )
    app.config["CORS_HEADERS"] = "Content-Type"
    CORS(app, resources={r"/*": {"origins": "*"}, r"/static/*": {"origins": "*"}})

    app.config["JWT_SECRET_KEY"] = "bsconsig"
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_HEADER_NAME"] = "Authorization"
    app.config["JWT_HEADER_TYPE"] = "Bearer"
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=2)

    jwt = JWTManager(app)
    
    # Namespaces registration
    api.add_namespace(user_us)
    api.add_namespace(login_ns)
    
    return app

