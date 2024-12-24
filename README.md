# Welding Application

This is a GL Hub Application for Welding Operations. The interface, built using Flask, is designed to be run on reTerminal DM devices that come with a Raspberry Pi CM4 + Touchscreen. The application also control one of the GPIO pins to lock/unlock the solenoid when performing welding operations.

## Getting Started

The device (reTerminal DM) will need to be flash with a custom balenaOS image with the necessarily custom device tree so that the OS can see the touchscreen (See Google Docs runbook for more details). Additionally, the touchscreen would also require a [special branch](https://github.com/groundlight/glhub/tree/reterminal-dm) of GL Hub that allows the custom kernal modules to be loaded in before initializing the `browser` container.

### Configuring the Application

The app requires the following environment variables:
- `WELD_APP_CONFIG`: This is the application config for the app and it follows the following JSON format which can be copied/pasted to the balena dashboard's device variables section:

```json
{
    "edge_endpoint": "EDGE_ENDPOINT_URL_OR_NONE_TO_USE_CLOUD",
    "ml_detector_id": "WELD_DETECTOR_ID", 
    "printer": {
        "printer_ip": "TAG_PRINTER_IP", 
        "printer_port": 9100, 
        "printer_timeout": 5, 
        "printer_paper_width": 2.25, 
        "printer_paper_length": 4.0,
        "printer_dpi": 203 
    }
}
```

- `WELD_CAMERA_CONFIG`: This is the camera config for each Jig Stations and it follows the following JSON format which can also be copied/pasted to the balena dashboard's device variables section:

```json
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
```

Each `camera_config` entries will need to match the configuration settings for `FrameGrab` so the cameras can be intiialized correctly.

- `WELD_APP_DATABASE_CONFIG`: This is the database config for fetching data from Google API Service.

```json
{
    "enabled": true,
    "service_account": {
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
```

The `service_account` section should match the credential JSON file downloaded from Google Cloud.

- `WELD_APP_SUPERVISOR_PASSWORD`: The supervisor password to lock/unlock the Jig Lock, default to None if not set

- `GROUNDLIGHT_API_TOKEN`: Groundlight API Token

- `LAUNCH_URL`: Set this to `http://router/hub/launch/1` to ensure that the device automatically redirects to the application main page when it is ready

### Creating Supervisor Password

If the you would like to only allow supervisors to lock/unlock the Jig Lock, you need to set the environment variable `WELD_APP_SUPERVISOR_PASSWORD` with the hashed password.

The hashed password can be created with the `generate_hash.py` script by running the following command:

```bash
poetry run python generate_hash.py PASSWORD
```

Copy the hashed password generated from the script to the environment variable:

```bash
export WELD_APP_SUPERVISOR_PASSWORD="HASHED_PASSWORD"
```

For balena deployment just copy the hashed password into the `Device Variables` tab.

## Local Testing

To run the app on your local machine just run this command:

```bash
poetry run python run.py
```

Note that the GPIO function will not work and the app will shows a warning about this.

For testing your own RTSP streams you can use VLC's command to start a RTSP server on your local machine.

```bash
brew install vlc
```

```bash
vlc -vvv YOUR_VIDEO_HERE --loop --sout '#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100,scodec=none}:rtp{sdp=rtsp://:8554/feed}' --sout-all --sout-keep
```

The video should be broadcasting on `rtsp://127.0.0.1:8554/feed` or on your machine assigned IP address.
