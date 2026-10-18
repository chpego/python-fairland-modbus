"""Asynchronous Modbus client for Fairland inverter pumps and heat pumps."""

from fairland_modbus.exceptions import FairlandConnectionError, FairlandError

__version__ = "0.0.0"

__all__ = [
    "FairlandConnectionError",
    "FairlandError",
    "__version__",
]
