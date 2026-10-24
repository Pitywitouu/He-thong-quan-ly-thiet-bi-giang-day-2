from __future__ import annotations
from abc import ABC, abstractmethod

from models.identifiable import IIdentifiable
from models.device_status import DeviceStatus
from exceptions.device_exceptions import DeviceNotReadyException, DeviceOperationException


class TeachingDevice(IIdentifiable, ABC):
    def __init__(self, id: str, name: str, storage_location: str) -> None:
        if not id or not id.strip():
            raise ValueError("Mã thiết bị (id) không được để trống.")
        if not name or not name.strip():
            raise ValueError("Tên thiết bị (name) không được để trống.")
        if not storage_location or not storage_location.strip():
            raise ValueError("Vị trí lưu trữ (storage_location) không được để trống.")

        self._id: str = id.strip()
        self._name: str = name.strip()
        self._storage_location: str = storage_location.strip()
        self._status: DeviceStatus = DeviceStatus.AVAILABLE

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def storage_location(self) -> str:
        return self._storage_location

    @property
    def status(self) -> DeviceStatus:
        return self._status

    def set_maintenance(self) -> None:
        self._status = DeviceStatus.UNDER_MAINTENANCE

    @abstractmethod
    def is_ready_for_use(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_default_priority_score(self) -> float:
        raise NotImplementedError

    def borrow(self) -> None:
        if not self.is_ready_for_use():
            raise DeviceNotReadyException(
                device_id=self._id,
                current_status=self._status,
                message=f"Không thể mượn thiết bị '{self._id}' vì thiết bị chưa sẵn sàng sử dụng (Trạng thái: {self._status}).",
            )
        self._status = DeviceStatus.BORROWED

    def return_device(self) -> None:
        if self._status != DeviceStatus.BORROWED:
            raise DeviceOperationException(
                f"Không thể trả thiết bị '{self._id}' vì thiết bị đang ở trạng thái '{self._status}', không phải 'Borrowed'."
            )
        self._status = DeviceStatus.AVAILABLE

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(id='{self._id}', name='{self._name}', "
            f"location='{self._storage_location}', status='{self._status}')"
        )
