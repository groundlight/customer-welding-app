import logging
import socket
import datetime

from weld import config

logger = logging.getLogger(__name__)

# Global lock status
lock_status = {"is_locked": False}


class PrinterService:
    """Service to interact with the thermal printer."""

    def __init__(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(config.WELD_APP_PRINTER_TIMEOUT)

        self.printer_ip = config.WELD_APP_PRINTER_IP
        self.printer_port = int(config.WELD_APP_PRINTER_PORT)

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
        width: float = config.WELD_APP_PRINTER_PAPER_WIDTH,
        length: float = config.WELD_APP_PRINTER_PAPER_LENGTH,
        dpi: int = config.WELD_APP_PRINTER_DPI,
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
            self.sock.settimeout(config.WELD_APP_PRINTER_TIMEOUT)
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
