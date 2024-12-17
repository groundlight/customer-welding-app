import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

import os

from weld import create_app

logger = logging.getLogger(__name__)

GLHUB_APP_PORT = int(os.getenv("GLHUB_APP_PORT", "8000"))


if __name__ == "__main__":
    app = create_app()

    logger.info(f"Running weld app on port {GLHUB_APP_PORT}")
    app.run(host="0.0.0.0", port=GLHUB_APP_PORT)
