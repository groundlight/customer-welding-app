import logging
import os

from weld import create_app

logger = logging.getLogger(__name__)

GLHUB_APP_PORT = int(os.getenv("GLHUB_APP_PORT", "8000"))
    

if __name__ == "__main__":
    app = create_app()
    
    # Adjust application proxy when running behind a reverse proxy (balenaCloud)
    # Check if we are running through balenaCloud (It is running on balena if the environment variable BALENA is set)
    if os.getenv("BALENA"):
        app.config["APPLICATION_ROOT"] = "/apps/app_1"
    
    logger.info(f"Running weld app on port {GLHUB_APP_PORT}")
    app.run(host="0.0.0.0", port=GLHUB_APP_PORT)