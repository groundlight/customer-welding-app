import sys
import logging

from flask import render_template, request, jsonify, current_app as app

from weld import backend

def create_default_context() -> dict:
    """Creates a default content for all the information that will be displayed to the Frontend.

    Returns a dictionary of all the web contents.
    """

    context = {
        "route": "/",
    }
    return context


@app.route("/api/lock-status", methods=["GET"])
def get_lock_status():
    """Endpoint to check the lock status."""
    
    return jsonify(backend.lock_status)


@app.route("/api/lock-status", methods=["POST"])
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


@app.route("/", methods=["GET", "POST"])
def index():
    """Load the index page of the website with camera preview."""

    context = create_default_context()

    return render_template("index.html", **context)
