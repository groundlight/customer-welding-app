import sys
import logging

from flask import render_template, request, Response, current_app as app

from weld import backend


def setup():
    """Setup logging configuration and create scheduler thread for ML reporting."""

    # Set logging configuration
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


setup()


def create_default_context(errors: list[str], warnings: list[str]) -> dict:
    """Creates a default content for all the information that will be displayed to the Frontend.

    Returns a dictionary of all the web contents.
    """

    context = {
        "api_status": True,
        "camera_status": True,
        "errors": errors,
        "warnings": warnings,
        "route": "/",
    }
    return context


@app.route("/", methods=["GET", "POST"])
def index():
    """Load the index page of the website with camera preview."""

    global play_sound

    errors: list[str] = []
    warnings: list[str] = []

    context = create_default_context(errors=errors, warnings=warnings)

    return render_template("index.html", **context)
