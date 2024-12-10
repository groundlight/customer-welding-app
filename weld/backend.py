import logging

from weld import config

logger = logging.getLogger(__name__)

# Global lock status
lock_status = {"is_locked": False}