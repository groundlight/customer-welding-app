import os
import logging

logger = logging.getLogger(__name__)

"""Load Environment Variables"""
WELD_APP_ML_DETECTOR_ID = os.getenv("WELD_APP_ML_DETECTOR_ID")  # ML Detector ID
WELD_APP_PRINTER_IP = os.getenv("WELD_APP_PRINTER_IP")  # Tag Printer IP
WELD_APP_PRINTER_PORT = int(os.getenv("WELD_APP_PRINTER_PORT"))  # Tag Printer Port
WELD_APP_PRINTER_TIMEOUT = int(os.getenv("WELD_APP_PRINTER_TIMEOUT", 5))  # Tag Printer Timeout, default 5 seconds
WELD_APP_PRINTER_PAPER_WIDTH = float(os.getenv("WELD_APP_PRINTER_PAPER_WIDTH", 2.25))  # Tag Printer Paper Width, default 2.25 inches
WELD_APP_PRINTER_PAPER_LENGTH = float(os.getenv("WELD_APP_PRINTER_PAPER_LENGTH", 4.00))  # Tag Printer Paper Length, default 4.00 inches
WELD_APP_PRINTER_DPI = int(os.getenv("WELD_APP_PRINTER_DPI", 203))  # Tag Printer DPI, default 203


def check_environment_variables() -> bool:
    """Check if all the required environment variables are set.

    Returns:
        bool: True if all the environment variables are set, False otherwise.
    """

    return (
        WELD_APP_ML_DETECTOR_ID
        and WELD_APP_PRINTER_IP
        and WELD_APP_PRINTER_PORT
        and WELD_APP_PRINTER_TIMEOUT
        and WELD_APP_PRINTER_PAPER_WIDTH
        and WELD_APP_PRINTER_PAPER_LENGTH
        and WELD_APP_PRINTER_DPI
    )
