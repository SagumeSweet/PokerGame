import uuid

from flask import Flask

from BluePrints import get_blueprint


def get_app_run(path: str = '') -> Flask:
    app = Flask(__name__)
    app.register_blueprint(get_blueprint(path))
    app.secret_key = str(uuid.uuid4())
    return app


if __name__ == "__main__":
    app_test = get_app_run('/test')
    app_test.run(debug=True)
