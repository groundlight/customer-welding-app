import sys
import logging
import time

from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app

from weld import backend

app = Flask(__name__)

def create_default_context() -> dict:
    """Creates a default content for all the information that will be displayed to the Frontend.

    Returns a dictionary of all the web contents.
    """

    context = {
        "LeftWelder": None,
        "RightWelder": None,
        "JigNumber": None,
        "ShiftNumber": None,
        "PartNumber": None,
        "ExpectedLeftWelds": None,
        "ExpectedRightWelds": None,
        "ActualPartNumber": None,
        "ActualLeftWelds": None,
        "ActualRightWelds": None,
        "ApplicationRoot": app.config["APPLICATION_ROOT"],
        "route": "/",
    }
    return context


@app.route("/api-lock-status", methods=["GET"])
def get_lock_status():
    """Endpoint to check the lock status."""

    return jsonify(backend.lock_status)


@app.route("/api-lock-status", methods=["POST"])
def set_lock_status():
    """Endpoint to update the lock status."""

    lock_status = backend.lock_status
    data = request.get_json()

    if "is_locked" in data:
        lock_status["is_locked"] = data["is_locked"]

        # TODO: Call backend to actually lock/unlock the device
        if lock_status["is_locked"]:
            app.logger.info("Locking the device")
        else:
            app.logger.info("Unlocking the device")

        app.logger.info(f"Lock status updated to: {'Locked' if data['is_locked'] else 'Unlocked'}")
        return jsonify({"message": "Lock status updated successfully"}), 200

    return jsonify({"error": "Invalid data"}), 400


@app.route("/api-weld-data", methods=["GET"])
def get_weld_data():
    """Endpoint to get the weld data."""

    # TODO: Call backend to get the weld data

    data = {
        "partNumber": "0123456789",
        "leftWeldCount": 20,
        "rightWeldCount": 20,
    }
    return jsonify(data)


@app.route("/", methods=["GET", "POST"])
def index():
    """Load the index page of the website with camera preview."""

    context = create_default_context()

    return render_template("index.html", **context)


@app.route("/part", methods=["GET", "POST"])
def part():
    """Load the part page of the website with camera preview."""

    context = create_default_context()

    if request.method == "POST":
        left_welder = request.form.get("left_welder")
        right_welder = request.form.get("right_welder")
        jig_number = request.form.get("jig_number")
        shift_number = request.form.get("shift_number")

        # Update the context with submitted data
        context.update(
            {
                "LeftWelder": left_welder,
                "RightWelder": right_welder,
                "JigNumber": jig_number,
                "ShiftNumber": shift_number,
            }
        )
        return render_template("part.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return render_template("part.html", **context)


@app.route("/process", methods=["GET", "POST"])
def process():
    """Load the process page of the website with ML result."""

    context = create_default_context()

    if request.method == "POST":
        left_welder = request.form.get("left_welder")
        right_welder = request.form.get("right_welder")
        jig_number = request.form.get("jig_number")
        shift_number = request.form.get("shift_number")
        part_number = request.form.get("part_number")
        expected_left_welds = request.form.get("expected_left_welds")
        expected_right_welds = request.form.get("expected_right_welds")

        # Update the context with submitted data
        context.update(
            {
                "LeftWelder": left_welder,
                "RightWelder": right_welder,
                "JigNumber": jig_number,
                "ShiftNumber": shift_number,
                "PartNumber": part_number,
                "ExpectedLeftWelds": expected_left_welds,
                "ExpectedRightWelds": expected_right_welds,
            }
        )

        # TODO: Call backend to start the ML to count the welds

        return render_template("process.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))


@app.route("/review", methods=["GET", "POST"])
def review():
    """Load the process page of the website with ML result."""

    context = create_default_context()

    if request.method == "POST":
        left_welder = request.form.get("left_welder")
        right_welder = request.form.get("right_welder")
        jig_number = request.form.get("jig_number")
        shift_number = request.form.get("shift_number")
        part_number = request.form.get("part_number")
        expected_left_welds = request.form.get("expected_left_welds")
        expected_right_welds = request.form.get("expected_right_welds")
        actual_left_welds = request.form.get("actual_left_welds")
        actual_right_welds = request.form.get("actual_right_welds")

        # Update the context with submitted data
        context.update(
            {
                "LeftWelder": left_welder,
                "RightWelder": right_welder,
                "JigNumber": jig_number,
                "ShiftNumber": shift_number,
                "PartNumber": part_number,
                "ExpectedLeftWelds": expected_left_welds,
                "ExpectedRightWelds": expected_right_welds,
                "ActualLeftWelds": actual_left_welds,
                "ActualRightWelds": actual_right_welds,
            }
        )

        return render_template("review.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))


@app.route("/print", methods=["GET", "POST"])
def print_tag():
    """Print the receipt of the welds."""

    context = create_default_context()

    if request.method == "POST":
        left_welder = request.form.get("left_welder")
        right_welder = request.form.get("right_welder")
        jig_number = request.form.get("jig_number")
        shift_number = request.form.get("shift_number")
        part_number = request.form.get("part_number")
        expected_left_welds = request.form.get("expected_left_welds")
        expected_right_welds = request.form.get("expected_right_welds")
        actual_part_number = request.form.get("actual_part_number")
        actual_left_welds = request.form.get("actual_left_welds")
        actual_right_welds = request.form.get("actual_right_welds")

        # Update the context with submitted data
        context.update(
            {
                "LeftWelder": left_welder,
                "RightWelder": right_welder,
                "JigNumber": jig_number,
                "ShiftNumber": shift_number,
                "PartNumber": part_number,
                "ExpectedLeftWelds": expected_left_welds,
                "ExpectedRightWelds": expected_right_welds,
                "ActualPartNumber": actual_part_number,
                "ActualLeftWelds": actual_left_welds,
                "ActualRightWelds": actual_right_welds,
            }
        )

        # TODO: Call backend to print the receipt

        return render_template("print.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))
