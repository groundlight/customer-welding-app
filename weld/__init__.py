import os

from flask import Flask, Blueprint


def create_app():
    weld_app = Flask(__name__)
    
    # Adjust application proxy when running behind a reverse proxy (balenaCloud)
    # Check if we are running through balenaCloud (It is running on balena if the environment variable BALENA is set)
    if os.getenv("BALENA"):
        weld_app.config["APPLICATION_ROOT"] = "/apps/app_1"
        api_bp = Blueprint("api", __name__, url_prefix="/apps/app_1/api")
        weld_app.register_blueprint(api_bp, url_prefix="/apps/app_1")

    with weld_app.app_context():
        from weld import app

    return weld_app