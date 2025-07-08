"""
__init__.py

Initializes the Flask app, registers blueprints, and sets config.
"""

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "elden_souls_secret"

    from .routes import main

    app.register_blueprint(main)

    return app
