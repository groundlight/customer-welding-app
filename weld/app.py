import bcrypt
from flask import Flask, render_template, request, jsonify, redirect, url_for, current_app

from weld import backend, config

app = Flask(__name__)

"""Initialize all backend services"""
jig_lock_service = backend.JigLockService()
printer_service = backend.PrinterService()
weld_count_service = backend.WeldCountService()
shift_service = backend.ShiftService()


def create_default_context() -> dict:
    """Creates a default content for all the information that will be displayed to the Frontend.

    Returns a dictionary of all the web contents.
    """

    context = {
        "TotalJigStations": None,
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
        "WeldStats": None,
        "Error": None,
    }
    return context


@app.route("/api/parts", methods=["GET"])
def get_parts():
    """Endpoint to fetch part numbers from the database."""
    database = {
        "ABC123": {"Left Weld Count": 5, "Right Weld Count": 2},
        "XYZ283": {"Left Weld Count": 2, "Right Weld Count": 0},
        "IJK238": {"Left Weld Count": 0, "Right Weld Count": 3},
        "DI39843NDz": {"Left Weld Count": 0, "Right Weld Count": 12},
    }
    return jsonify(database)


@app.route("/api/lock-status", methods=["GET"])
def get_lock_status():
    """Endpoint to check the lock status."""

    return jsonify(jig_lock_service.lock_status_json)


@app.route("/api/password-required", methods=["GET"])
def is_password_required():
    """Endpoint to check if the password is required."""

    if config.supervisor_password is None or config.supervisor_password == "":
        return jsonify({"password_required": False})

    return jsonify({"password_required": True})


@app.route("/api/lock-status", methods=["POST"])
def set_lock_status():
    """Endpoint to update the lock status."""

    data = request.get_json()

    # Check if the password is correct
    if config.supervisor_password is not None and config.supervisor_password != "":
        if "password" not in data or not bcrypt.checkpw(password=data["password"].encode(), hashed_password=config.supervisor_password.encode()):
            app.logger.warning("Incorrect password attempt")
            return jsonify({"error": "Invalid password"}), 403

    if "is_locked" in data:
        if data["is_locked"]:
            app.logger.info("Locking the device")
            jig_lock_service.lock()
        else:
            app.logger.info("Unlocking the device")
            jig_lock_service.unlock()

        app.logger.info(f"Lock status updated to: {'Locked' if data['is_locked'] else 'Unlocked'}")
        return jsonify({"message": "Lock status updated successfully"}), 200

    return jsonify({"error": "Invalid data"}), 400


@app.route("/api/weld-data", methods=["GET"])
def get_weld_data():
    """Endpoint to get the weld data."""

    return jsonify(weld_count_service.get_weld_data())


@app.route("/", methods=["GET", "POST"])
def index():
    """Load the index page of the website with camera preview."""

    context = create_default_context()
    weld_count_service.stop_weld_count()

    # Get total number of Jig Stations
    total_jig_stations = len(config.camera_config.jig_stations)
    context["TotalJigStations"] = total_jig_stations

    return render_template("index.html", **context)


@app.route("/part", methods=["GET", "POST"])
def part():
    """Load the part page of the website with camera preview."""

    context = create_default_context()
    weld_count_service.stop_weld_count()

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

        # Start the shift
        shift_service.start_shift(left_welder_name=left_welder, right_welder_name=right_welder, jig_number=jig_number, shift_number=shift_number)

        return render_template("part.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))


@app.route("/process", methods=["GET", "POST"])
def process():
    """Load the process page of the website with ML result."""

    context = create_default_context()
    weld_count_service.stop_weld_count()

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

        # Lock the jig
        jig_lock_service.lock()

        # Start weld count ML
        weld_count_service.start_weld_count(part_number=part_number, jig_number=int(jig_number))

        return render_template("process.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))


@app.route("/review", methods=["GET", "POST"])
def review():
    """Load the process page of the website with ML result."""

    context = create_default_context()
    weld_count_service.stop_weld_count()

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
    weld_count_service.stop_weld_count()

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

        # Add the welds to the database
        shift_service.update_stats(part_number=actual_part_number)

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
                "WeldStats": shift_service.get_stats(),
            }
        )

        # Unlock the jig
        jig_lock_service.unlock()

        if not printer_service.print_tag(
            shift=int(shift_number),
            jig=int(jig_number),
            part_number=part_number,
            left_count=int(actual_left_welds),
            right_count=int(actual_right_welds),
            left_welder=left_welder,
            right_welder=right_welder,
        ):
            context["Error"] = "Failed to print the tag. Please try again."

        return render_template("print.html", **context)

    else:
        # Redirect back to the index page if the request is not POST (no login information received)
        return redirect(url_for("index"))
