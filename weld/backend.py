import socket
import logging
import datetime
import threading
from groundlight import Groundlight
from framegrab import FrameGrabber

from weld.config import app_config, camera_config

logger = logging.getLogger(__name__)

# Global lock status
lock_status = {"is_locked": False}


class WeldCountService:
    """Service to send ML request to Groundlight and count the number of welds."""

    def __init__(self) -> None:
        self.gl = Groundlight()
        self.detector = self.gl.get_detector(id=app_config.ml_detector_id)
        self.weld_data = {
            "partNumber": None,
            "leftWeldCount": 0,
            "rightWeldCount": 0,
        }

        # Thread control
        self.is_running = False
        self.thread = None

    def get_weld_data(self) -> dict:
        return self.weld_data

    def start_weld_count(self, part_number: str, jig_number: int) -> None:
        """Start the weld count for the given part number.

        Args:
            part_number (str): Part number to start the weld count.
            jig_number (int): Jig number for the weld (to determine the RTSP camera for ML).
        """

        self.weld_data["partNumber"] = part_number
        self.weld_data["leftWeldCount"] = 0
        self.weld_data["rightWeldCount"] = 0

        self.is_running = True

        # Call weld_count_thread with jig_number as a thread
        if self.thread is not None or self.is_running:
            logger.info("Stopping previous weld count thread")
            self.is_running = False
            self.thread.join()
            self.thread = None

        self.thread = threading.Thread(target=self.weld_count_thread, args=(jig_number,), daemon=True)

    def stop_weld_count(self) -> None:
        """Stop the weld count thread."""

        self.is_running = False

        if self.thread is not None:
            self.thread.join()
            self.thread = None

            self.weld_data["partNumber"] = None
            self.weld_data["leftWeldCount"] = 0
            self.weld_data["rightWeldCount"] = 0

    def weld_count_thread(self, jig_number: int) -> None:
        """Thread to count the number of welds for the given jig number.

        Args:
            jig_number (int): Jig number for the weld (to determine the RTSP camera for ML).
        """

        # Get the camera configuration for the jig number
        jig_camera_config = camera_config.jig_stations[jig_number].camera_config
        grabber = FrameGrabber.create_grabber_yaml(jig_camera_config)

        left_weld_has_flash = False
        right_weld_has_flash = False

        while self.is_running:
            frame = grabber.grab()

            # Cut the frame in half to get the left and right welds
            half_width = frame.shape[1] // 2
            left_frame = frame[:, :half_width]
            right_frame = frame[:, half_width:]

            # Send the left and right frames to the detector
            iq_left = self.gl.ask_async(detector=self.detector, image=left_frame)
            iq_right = self.gl.ask_async(detector=self.detector, image=right_frame)

            # Poll for result
            iq_left = self.gl.wait_for_confident_result(image_query=iq_left, timeout_sec=15)
            iq_right = self.gl.wait_for_confident_result(image_query=iq_right, timeout_sec=15)

            # Update the weld count
            if iq_left.result.label == "YES" and not left_weld_has_flash:
                self.weld_data["leftWeldCount"] += 1
                left_weld_has_flash = True
            else:
                left_weld_has_flash = False

            if iq_right.result.label == "YES" and not right_weld_has_flash:
                self.weld_data["rightWeldCount"] += 1
                right_weld_has_flash = True
            else:
                right_weld_has_flash = False


class PrinterService:
    """Service to interact with the thermal printer."""

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(app_config.printer.printer_timeout)

        self.printer_ip = app_config.printer.printer_ip
        self.printer_port = int(app_config.printer.printer_port)

    def _create_tag(
        self,
        date: str,
        shift: int,
        jig: int,
        part_number: str,
        left_count: int,
        right_count: int,
        left_welder: str,
        right_welder: str,
        width: float = app_config.printer.printer_paper_width,
        length: float = app_config.printer.printer_paper_length,
        dpi: int = app_config.printer.printer_dpi,
    ) -> str:
        """
        Create a ZPL string to print the formatted tag with consistent font size and dynamic centering.

        Args:
            date (str): Date of the weld in (MM/DD/YY).
            shift (int): Shift number.
            jig (int): Jig number.
            part_number (str): Part number.
            left_count (int): Left weld count.
            right_count (int): Right weld count.
            left_welder (str): Left welder name.
            right_welder (str): Right welder name.
            width (float, optional): Width of the tag in inches. Defaults to 2.25.
            length (float, optional): Length of the tag in inches. Defaults to 4.00.
            dpi (int, optional): Dots per inch of the printer. Defaults to 203.

        Returns:
            str: ZPL string to print the formatted tag.
        """
        # Calculate paper dimensions in dots
        width_dots = int(width * dpi)
        length_dots = int(length * dpi)

        # Font size for consistency
        font_size = 30

        # Calculate horizontal center
        center_x = width_dots // 2

        # Calculate total weld count
        total_count = left_count + right_count

        # Create the ZPL string
        zpl = f"""
        ^XA
        ^PW{width_dots}
        ^LL{length_dots}
        ^CF0,{font_size}

        ^FO20,30^FDDate: {date}^FS
        ^FO{width_dots - 150},30^FDShift: {shift}^FS

        ^CF0,{font_size}
        ^FO{center_x - 50},80^FDJig #^FS
        ^FO{center_x - 50},120^FD{jig}^FS

        ^FO{center_x - 100},180^FDPart Number^FS
        ^FO{center_x - 100},220^FD{part_number}^FS

        ^CF0,{font_size}
        ^FO20,280^FDLeft Weld^FS
        ^FO{width_dots - 200},280^FDRight Weld^FS
        ^FO20,320^FDCount^FS
        ^FO{width_dots - 200},320^FDCount^FS
        ^FO20,360^FD{left_count}^FS
        ^FO{width_dots - 200},360^FD{right_count}^FS

        ^CF0,{font_size}
        ^FO{center_x - 100},420^FDTotal Weld Count^FS
        ^FO{center_x - 50},480^FD{total_count}^FS

        ^CF0,{font_size}
        ^FO20,540^FDLeft Welder^FS
        ^FO{width_dots - 200},540^FDRight Welder^FS
        ^FO20,580^FD{left_welder}^FS
        ^FO{width_dots - 200},580^FD{right_welder}^FS
        ^XZ
        """

        return zpl

    def _send_to_printer(self, zpl: str) -> bool:
        """
        Send the ZPL string to the printer.

        Args:
            zpl (str): ZPL string to print.

        Returns:
            bool: True if the data was sent successfully, False otherwise.
        """

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(app_config.printer.printer_timeout)
            self.sock.connect((self.printer_ip, self.printer_port))
            self.sock.send(zpl.encode())
            self.sock.close()
        except Exception as e:
            logger.error(f"Failed to send data to the printer: {e}", exc_info=True)
            return False

        return True

    def print_tag(
        self,
        shift: int,
        jig: int,
        part_number: str,
        left_count: int,
        right_count: int,
        left_welder: str,
        right_welder: str,
    ) -> bool:
        """
        Print the formatted tag with the weld data.

        Args:
            shift (int): Shift number.
            jig (int): Jig number.
            part_number (str): Part number.
            left_count (int): Left weld count.
            right_count (int): Right weld count.
            left_welder (str): Left welder name.
            right_welder (str): Right welder name.

        Returns:
            bool: True if the tag was printed successfully, False otherwise.
        """

        # Get the current date and format it to MM/DD/YY
        date = datetime.datetime.now().strftime("%m/%d/%y")

        zpl = self._create_tag(
            date=date,
            shift=shift,
            jig=jig,
            part_number=part_number,
            left_count=left_count,
            right_count=right_count,
            left_welder=left_welder,
            right_welder=right_welder,
        )

        return self._send_to_printer(zpl)
