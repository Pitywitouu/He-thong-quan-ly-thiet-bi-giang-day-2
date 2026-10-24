from enum import Enum


class DeviceStatus(str, Enum):
    AVAILABLE = "Available"
    BORROWED = "Borrowed"
    UNDER_MAINTENANCE = "UnderMaintenance"

    def __str__(self) -> str:
        return self.value
