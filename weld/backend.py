import logging

from weld import config

logger = logging.getLogger(__name__)

# Global lock status1
lock_status = {"is_locked": False}