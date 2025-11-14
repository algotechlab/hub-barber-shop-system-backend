from dotenv import load_dotenv

from src.external import create_app
from src.core.config import config_by_name, flask_env
from src.db.extensions import verify_database_connection

load_dotenv()


class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ.update({"Id": 3})
        environ.update({"email": "hedrisgts@gmail.com"})
        environ.update({"company_id": 4})
        return self.app(environ, start_response)


app = create_app()
app.wsgi_app = Middleware(app.wsgi_app)

verify_database_connection(app)

if __name__ == "__main__":
    app.run(
        port=config_by_name[flask_env].PORT,
        debug=config_by_name[flask_env].DEBUG,
        host="0.0.0.0",
    )
