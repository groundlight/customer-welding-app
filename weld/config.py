import os
import sys
import logging
from pydantic import Field, BaseModel

logger = logging.getLogger(__name__)

SAMPLE_APP_CONFIG = """
{
    "ml_detector_id": "DETECTOR_ID", 
    "printer": {
        "printer_ip": "PRINTER_IP", 
        "printer_port": 9100, 
        "printer_timeout": 5, 
        "printer_paper_width": 2.25, 
        "printer_paper_length": 4.0,
        "printer_dpi": 203 
    }
}
"""

SAMPLE_APP_CAMERA_CONFIG = """
{
    "jig_stations": {
        "1": {
            "camera_config": "name: Jig Station 1 Camera\ninput_type: rtsp\nid:\n  rtsp_url: RTSP_1"
        }, 
        "2": {
            "camera_config": "name: Jig Station 2 Camera\ninput_type: rtsp\nid:\n  rtsp_url: RTSP_2"
        }
    }
}
"""

app_config_raw = os.getenv("WELD_APP_CONFIG", None)
app_config = None

camera_config_raw = os.getenv("WELD_APP_CAMERA_CONFIG", None)
camera_config = None


class PrinterConfig(BaseModel):
    printer_ip: str = Field(..., description="Tag Printer IP")
    printer_port: int = Field(..., description="Tag Printer Port")
    printer_timeout: int = Field(5, description="Tag Printer Timeout in seconds, default 5")
    printer_paper_width: float = Field(2.25, description="Tag Printer Paper Width in inches, default 2.25")
    printer_paper_length: float = Field(4.00, description="Tag Printer Paper Length in inches, default 4.00")
    printer_dpi: int = Field(203, description="Tag Printer DPI, default 203")


class AppConfig(BaseModel):
    edge_endpoint: str | None = Field(None, description="The edge-endpoint IP address for local inference, default None for cloud inference")
    ml_detector_id: str = Field(..., description="ML Detector ID")
    printer: PrinterConfig


class JigStationConfig(BaseModel):
    camera_config: dict = Field(..., description="Camera configuration Dict for FrameGrab")


class AppCameraConfig(BaseModel):
    jig_stations: dict[int, JigStationConfig] = Field(..., description="Mapping of jig stations to their raw camera configuration strings")


# Load configuration
try:
    app_config = AppConfig.model_validate_json(app_config_raw)
    camera_config = AppCameraConfig.model_validate_json(camera_config_raw)
    logger.info("Configuration loaded successfully!")
except Exception as e:
    logger.error(f"Error loading configuration: {e}", exc_info=True)
    sys.exit(1)
