from __future__ import annotations
from typing import Iterable, Set

from models.teaching_device import TeachingDevice
from models.device_status import DeviceStatus


class AirConditionerRemote(TeachingDevice):
    def __init__(
        self,
        id: str,
        name: str,
        storage_location: str,
        compatible_rooms: Iterable[str],
    ) -> None:
        super().__init__(id, name, storage_location)
        self._compatible_rooms: Set[str] = {room.strip() for room in compatible_rooms if room and room.strip()}

    @property
    def compatible_rooms(self) -> frozenset[str]:
        return frozenset(self._compatible_rooms)

    def is_compatible_with(self, room_id: str) -> bool:
        if not room_id:
            return False
        return room_id.strip() in self._compatible_rooms

    def is_ready_for_use(self) -> bool:
        return self.status == DeviceStatus.AVAILABLE

    def get_default_priority_score(self) -> float:
        return 100.0 if (self.is_ready_for_use() and len(self._compatible_rooms) > 0) else 0.0

    def __repr__(self) -> str:
        rooms = list(self._compatible_rooms)
        return (
            f"AirConditionerRemote(id='{self.id}', name='{self.name}', "
            f"rooms={rooms}, status='{self.status}')"
        )
