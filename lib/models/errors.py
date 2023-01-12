class HomeError(BaseException):
    """Base error class for Home library"""

    pass


class DuplicateDeviceError(HomeError):
    """Raised when device name or mac is non-unique"""

    pass
