"""
__init__.py

Initializes the Flask app, registers blueprints, and sets config.
"""

from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "elden_souls_secret"

    # Cache static assets (videos, images, audio, fonts) for a year.
    # Without this, the dark-souls-bonfire.mp4 background video and the
    # battle/area images re-fetch on every full-page navigation, which is
    # the main source of the visible stutter between screens.
    # NOTE: Flask does NOT auto-append a cache-busting query string to
    # url_for('static', ...) — if you replace an asset file in place with
    # the same filename, browsers may keep serving the old cached version
    # for up to a year. Rename changed assets (or add a manual ?v=N) when
    # swapping art/audio files.
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 31536000  # 1 year, in seconds

    from .routes import main

    app.register_blueprint(main)

    return app