from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from models.device_status import DeviceStatus


class TeachingDeviceException(Exception):
    pass


class DuplicateIdException(TeachingDeviceException):

    def __init__(self, duplicate_id: str, message: Optional[str] = None):
        self.duplicate_id = duplicate_id
        msg = message or f"Thiết bị với mã '{duplicate_id}' đã tồn tại trong hệ thống."
        super().__init__(msg)


class NoSuitableItemException(TeachingDeviceException):
    def __init__(self, message: Optional[str] = None):
        super().__init__(message or "Không tìm thấy thiết bị nào phù hợp với yêu cầu.")


class DeviceNotReadyException(TeachingDeviceException):
    def __init__(self, device_id: str, current_status: DeviceStatus, message: Optional[str] = None):
        self.device_id = device_id
        self.current_status = current_status
        msg = message or f"Thiết bị '{device_id}' hiện không sẵn sàng để sử dụng (Trạng thái hiện tại: {current_status})."
        super().__init__(msg)


class DeviceOperationException(TeachingDeviceException):
    pass
