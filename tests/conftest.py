import sys
from unittest.mock import Mock

# Mock RPi.GPIO globally
sys.modules["RPi.GPIO"] = Mock()
