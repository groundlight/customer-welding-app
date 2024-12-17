# Welding Application

This is a GL Hub Application for Welding Operations. The interface, built using Flask, is designed to be run on reTerminal DM devices that come with a Raspberry Pi CM4 + Touchscreen. The application also control one of the GPIO pins to lock/unlock the solenoid when performing welding operations.

## Getting Started

The device (reTerminal DM) will need to be flash with a custom balenaOS image with the necessarily custom device tree so that the OS can see the touchscreen (See Google Docs runbook for more details). Additionally, the touchscreen would also require a [special branch](https://github.com/groundlight/glhub/tree/reterminal-dm) of GL Hub that allows the custom kernal modules to be loaded in before initializing the `browser` container.

### Configuring the Application

The app requires the following environment variables:
- `WELD_APP_CONFIG`: This is the application config for the app and it follows the following JSON format which can be copied/pasted to the balena dashboard's device variables section:

```json
{
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
            "camera_config": "RTSP_CONFIGURATION_FRAMEGRAB_FORMAT"
        }, 
        "2": {
            "camera_config": "RTSP_CONFIGURATION_FRAMEGRAB_FORMAT"
        }
    }
}
```

- `GROUNDLIGHT_API_TOKEN`: Groundlight API Token

- `LAUNCH_URL`: Set this to `http://router/hub/launch/1` to ensure that the device automatically redirects to the application main page when it is ready

## Local Testing

To run the app on your local machine just run this command:

```bash
poetry run python run.py
```

Note that the GPIO function will not work and the app will shows a warning about this.
