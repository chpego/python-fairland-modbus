"""Asynchronous Modbus client for Fairland inverter pumps and heat pumps."""

from importlib.metadata import version

from fairland_modbus.exceptions import (
    FairlandConnectionError,
    FairlandError,
    FairlandRefusedError,
    FairlandTimeoutError,
    NotAFairlandDeviceError,
)

# The release workflow stamps the version into pyproject.toml from the git
# tag, so the installed distribution metadata is the single source of truth.
__version__ = version("fairland-modbus")

__all__ = [
    "FairlandConnectionError",
    "FairlandError",
    "FairlandRefusedError",
    "FairlandTimeoutError",
    "NotAFairlandDeviceError",
    "__version__",
]
