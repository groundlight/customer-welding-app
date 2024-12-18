import socket
import logging
import datetime
import threading
from groundlight import Groundlight
from framegrab import FrameGrabber

from weld.config import app_config, camera_config

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO

    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False
    logger.warning("RPi.GPIO not available on this platform. GPIO functions will not work.")


class SaturatingCounter:
    """2-state 1-bit Saturating Counter."""

    def __init__(self):
        # Initialize the counter, increase states when needed
        self.state = 0  # Counter starts at 0
        self.max_state = 1  # Saturates at 1
        self.min_state = 0  # Lower bound at 0

    def update(self, condition: bool) -> str:
        """
        Update the counter based on condition.

        Args:
            condition (bool): True if input == "YES", False otherwise.

        Returns:
            str: "YES" if state >= 2, "NO" otherwise.
        """

        if condition:  # Increment on "YES"
            self.state = min(self.max_state, self.state + 1)
        else:  # Decrement on "NO"
            self.state = max(self.min_state, self.state - 1)

        # Return the state result based on ranges
        return "YES" if self.state >= 1 else "NO"


class JigLockService:
    """Service to lock and unlock the jig station."""

    def __init__(self) -> None:
        self.is_locked = False
        self.lock_status_json = {"is_locked": self.is_locked}

        # TODO: Make this configurable in the config file
        self.GPIO_PIN = 24

        # Setup GPIO
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.GPIO_PIN, GPIO.OUT)

            # Get current state of the GPIO pin
            try:
                current_state = GPIO.input(self.GPIO_PIN)
                self.is_locked = current_state == GPIO.HIGH
                self.lock_status_json["is_locked"] = self.is_locked
            except Exception as e:
                logger.error(f"Failed to read GPIO pin state: {e}", exc_info=True)
                self.is_locked = False  # Fail-safe default

    def lock(self) -> bool:
        """Lock the jig station.

        Returns:
            bool: True if the jig station was locked successfully, False otherwise.
        """

        if not GPIO_AVAILABLE:
            logger.warning("GPIO functionality is unavailable. Cannot lock.")
            return False

        try:
            GPIO.output(self.GPIO_PIN, GPIO.HIGH)
            if GPIO.input(self.GPIO_PIN) == GPIO.HIGH:
                self.is_locked = True
                self.lock_status_json["is_locked"] = self.is_locked
                logger.info("Jig station locked successfully")
                return True
            else:
                logger.error("Failed to verify pin state after locking")
                return False
        except Exception as e:
            logger.error(f"Failed to lock the jig station: {e}", exc_info=True)
            return False

    def unlock(self) -> bool:
        """Unlock the jig station.

        Returns:
            bool: True if the jig station was unlocked successfully, False otherwise.
        """

        if not GPIO_AVAILABLE:
            logger.warning("GPIO functionality is unavailable. Cannot unlock.")
            return False

        try:
            GPIO.output(self.GPIO_PIN, GPIO.LOW)
            if GPIO.input(self.GPIO_PIN) == GPIO.LOW:
                self.is_locked = False
                self.lock_status_json["is_locked"] = self.is_locked
                logger.info("Jig station unlocked successfully")
                return True
            else:
                logger.error("Failed to verify pin state after unlocking")
                return False
        except Exception as e:
            logger.error(f"Failed to unlock the jig station: {e}", exc_info=True)
            return False


class WeldCountService:
    """Service to send ML request to Groundlight and count the number of welds."""

    def __init__(self) -> None:
        if app_config.edge_endpoint is not None and app_config.edge_endpoint != "" and app_config.edge_endpoint != "None":
            logger.info(f"Using edge-endpoint: {app_config.edge_endpoint}")
            self.gl = Groundlight(endpoint=app_config.edge_endpoint)
        else:
            logger.info("Using default Groundlight endpoint")
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
        """Get the weld data.

        Returns:
            dict: Weld data dictionary with part number, left weld count, and right weld count.
        """

        return self.weld_data

    def start_weld_count(self, part_number: str, jig_number: int) -> None:
        """Start the weld count for the given part number.

        Args:
            part_number (str): Part number to start the weld count.
            jig_number (int): Jig number for the weld (to determine the RTSP camera for ML).
        """

        # Call weld_count_thread with jig_number as a thread
        if self.thread is not None or self.is_running:
            logger.info("Stopping previous weld count thread")
            self.is_running = False
            self.thread.join()
            self.thread = None

        self.weld_data["partNumber"] = part_number
        self.weld_data["leftWeldCount"] = 0
        self.weld_data["rightWeldCount"] = 0

        self.is_running = True

        logger.info(f"Starting weld count for part number: {part_number}")
        self.thread = threading.Thread(target=self.weld_count_thread, args=(jig_number,), daemon=True)
        self.thread.start()

    def stop_weld_count(self) -> None:
        """Stop the weld count thread."""

        self.is_running = False

        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def weld_count_thread(self, jig_number: int) -> None:
        """Thread to count the number of welds for the given jig number."""

        # Camera setup
        jig_camera_config = camera_config.jig_stations[jig_number].camera_config
        grabber = FrameGrabber.create_grabber(jig_camera_config)
        logger.debug(f"Initialized FrameGrab with camera config: {grabber.config}")

        # Flash states and counters
        left_weld_counter = SaturatingCounter()
        right_weld_counter = SaturatingCounter()
        left_weld_has_flash = False
        right_weld_has_flash = False

        while self.is_running:
            logging.info("Grabbing frame")

            try:
                frame = grabber.grab()
            except Exception as e:
                logger.error(f"Failed to grab frame: {e}", exc_info=True)
                grabber.release()
                grabber = FrameGrabber.create_grabber(jig_camera_config)
                continue

            logger.info("Frame grabbed")

            # Split frame into left and right
            half_width = frame.shape[1] // 2
            left_frame = frame[:, :half_width]
            right_frame = frame[:, half_width:]

            logger.info("Asking ML for weld detection")

            try:
                iq_left = self.gl.ask_async(detector=self.detector, image=left_frame)
                iq_right = self.gl.ask_async(detector=self.detector, image=right_frame)

                iq_left = self.gl.wait_for_ml_result(image_query=iq_left, timeout_sec=30)
                iq_right = self.gl.wait_for_ml_result(image_query=iq_right, timeout_sec=30)
            except Exception as e:
                logger.error(f"Failed to get ML result: {e}", exc_info=True)
                continue

            logger.info("ML result received")

            # Left weld logic with 2-bit counter
            left_result = left_weld_counter.update(iq_left.result.label == "YES")
            if left_result == "YES" and not left_weld_has_flash:
                self.weld_data["leftWeldCount"] += 1
                left_weld_has_flash = True
                logger.info("Left weld flash detected, count incremented.")
            elif left_result == "NO":
                left_weld_has_flash = False

            # Right weld logic with 2-bit counter
            right_result = right_weld_counter.update(iq_right.result.label == "YES")
            if right_result == "YES" and not right_weld_has_flash:
                self.weld_data["rightWeldCount"] += 1
                right_weld_has_flash = True
                logger.info("Right weld flash detected, count incremented.")
            elif right_result == "NO":
                right_weld_has_flash = False

            logger.info("Single frame processed")

        # Release the grabber before thread exit
        grabber.release()


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
            logger.info(f"Sending data to the printer with IP: {self.printer_ip} and Port: {self.printer_port}")
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(app_config.printer.printer_timeout)
            self.sock.connect((self.printer_ip, self.printer_port))
            self.sock.send(zpl.encode())
            self.sock.close()
        except Exception as e:
            logger.error(f"Failed to send data to the printer: {e}", exc_info=True)
            return False

        logger.info("Data sent to the printer successfully!")
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
