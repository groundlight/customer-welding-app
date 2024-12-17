import unittest
from groundlight import Groundlight
from weld import backend


class TestSaturatingCounter(unittest.TestCase):
    def test_update(self):
        """Test the update method of the SaturatingCounter class."""

        counter = backend.SaturatingCounter()

        assert counter.update(False) == "NO"
        assert counter.update(True) == "YES"
