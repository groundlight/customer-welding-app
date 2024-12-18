import sys
import unittest

from unittest.mock import Mock

# Mock RPi.GPIO if unavailable
if "RPi.GPIO" not in sys.modules:
    sys.modules["RPi.GPIO"] = Mock()

from weld import backend


class TestSaturatingCounter(unittest.TestCase):
    def test_update(self):
        """Test the update method of the SaturatingCounter class."""

        counter = backend.SaturatingCounter()

        assert counter.update(False) == "NO"
        assert counter.update(True) == "YES"
