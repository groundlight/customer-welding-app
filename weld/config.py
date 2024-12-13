"""Pydantic models for settings and API status."""

import sys
import yaml
import logging

from pathlib import Path
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


class ML(BaseModel):
    detector_name: str  # Name of the detector
    query: str  # Query question for the detector
    confidence_threshold: (
        float  # Confidence threshold for ML resporting confident or unclear answer
    )
    trigger_interval_seconds: int  # Time between each image query


class Timeout(BaseModel):
    ml_api_timeout_seconds: int  # ML timeout in seconds before continuing


class Settings(BaseModel):
    ml: ML
    timeout: Timeout


def load_settings(file_path: str) -> Settings:
    """Load settings from YAML file

    Returns pydantic validated data structure
    """

    path = Path(file_path)
    try:
        with path.open("r") as file:
            data = yaml.safe_load(file)
        return Settings(**data)
    except ValidationError as e:
        logger.error(f"Load config failed: ", exc_info=True)
        sys.exit(1)