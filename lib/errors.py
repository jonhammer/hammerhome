class HammerHomeException(BaseException):
    pass


class UnknownDeviceType(HammerHomeException):
    pass


class UnknownRoom(HammerHomeException):
    pass


class DeviceNotFound(HammerHomeException):
    pass


class MultipleDevicesFound(HammerHomeException):
    pass
