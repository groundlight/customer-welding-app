import os

from flask import Flask


def create_app():
    weld_app = Flask(__name__)

    with weld_app.app_context():
        from weld import app

    return weld_app