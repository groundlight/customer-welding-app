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
            "camera_config": {
                "name": "Jig Station 1 Camera",
                "input_type": "rtsp",
                "id": {
                    "rtsp_url": "RTSP_URL_HERE"
                },
                "options": {
                    "keep_connection_open": true,
                    "crop": {
                        "relative": {
                            "left": 0.0,
                            "right": 1.0
                        }
                    }
                }
            }
        }, 
        "2": {
            "camera_config": {
                "name": "Jig Station 2 Camera",
                "input_type": "rtsp",
                "id": {
                    "rtsp_url": "RTSP_URL_HERE"
                },
                "options": {
                    "keep_connection_open": true,
                    "crop": {
                        "relative": {
                            "left": 0.0,
                            "right": 1.0
                        }
                    }
                }
            }
        }
    }
}
"""

SAMPLE_APP_DATABASE_CONFIG = """
{
    "enabled": true,
    "service_account - MODIFY THIS ENTIRE SECTION WITH JSON DOWNLOADED FROM GOOGLE CLOUD": {
        "type": "service_account",
        "project_id": "PROJECT_ID_HERE",
        "private_key_id": "PRIVATE_KEY_ID_HERE",
        "private_key": "PRIVATE_KEY_HERE",
        "client_email": "CLIENT_EMAIL_HERE",
        "client_id": "CLIENT_ID_HERE",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "CLIENT_CERT_URL_HERE",
        "universe_domain": "googleapis.com"
    },
    "database_id": "YOUR_DATABASE_ID_HERE",
    "database_range": "Sheet1!A2:C"
}
"""

device_id = os.getenv("WELD_APP_DEVICE_ID", "Default")

app_config_raw = os.getenv("WELD_APP_CONFIG", None)
app_config = None

camera_config_raw = os.getenv("WELD_APP_CAMERA_CONFIG", None)
camera_config = None

database_config_raw = os.getenv("WELD_APP_DATABASE_CONFIG", None)
database_config = None

supervisor_password = os.getenv("WELD_APP_SUPERVISOR_PASSWORD", None)


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


class DatabaseConfig(BaseModel):
    enabled: bool = Field(False, description="Enable Part Number Database (Default: False)")
    service_account: dict = Field(..., description="Service Account for Part Number Database")
    database_id: str = Field(..., description="Database ID for Part Number Database (Google Spreadsheet ID)")
    database_range: str = Field(..., description="Database Range for Part Number Database (Google Spreadsheet Range)")


# Load configuration
try:
    app_config = AppConfig.model_validate_json(app_config_raw)
    camera_config = AppCameraConfig.model_validate_json(camera_config_raw)
    database_config = DatabaseConfig.model_validate_json(database_config_raw)
    logger.info("Configuration loaded successfully!")
except Exception as e:
    logger.error(f"Error loading configuration: {e}", exc_info=True)
    sys.exit(1)
