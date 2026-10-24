from __future__ import annotations

from models.teaching_device import TeachingDevice
from models.device_status import DeviceStatus


class ProjectorRemote(TeachingDevice):
    def __init__(self, id: str, name: str, storage_location: str, battery_level: int) -> None:
        super().__init__(id, name, storage_location)
        if not (0 <= battery_level <= 100):
            raise ValueError(f"Mức pin phải trong khoảng 0 đến 100, nhận được: {battery_level}")
        self._battery_level: int = battery_level

    @property
    def battery_level(self) -> int:
        return self._battery_level

    def is_ready_for_use(self) -> bool:
        return self.status == DeviceStatus.AVAILABLE and self._battery_level >= 20

    def get_default_priority_score(self) -> float:
        return float(self._battery_level)

    def __repr__(self) -> str:
        return (
            f"ProjectorRemote(id='{self.id}', name='{self.name}', "
            f"battery={self._battery_level}%, status='{self.status}')"
        )
