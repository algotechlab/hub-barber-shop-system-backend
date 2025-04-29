from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restx import Api


def create_app():
    
    app = Flask(__name__)
    
    return app

