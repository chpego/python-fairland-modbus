"""Exceptions raised by the Fairland Modbus client."""


class FairlandError(Exception):
    """Base error for the library: a bad value or undecodable data."""


class FairlandConnectionError(FairlandError):
    """The Modbus transport failed while talking to the device."""
