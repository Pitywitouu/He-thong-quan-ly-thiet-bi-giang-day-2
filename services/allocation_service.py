from __future__ import annotations
from typing import Callable, Generic, List, Optional, TypeVar

from models.teaching_device import TeachingDevice
from repositories.in_memory_repository import IRepository
from strategies.selection_strategy import ISelectionStrategy
from exceptions.device_exceptions import NoSuitableItemException

T = TypeVar("T", bound=TeachingDevice)


class AllocationService(Generic[T]):
    def __init__(self, repository: IRepository[T], strategy: ISelectionStrategy[T]) -> None:
        if repository is None:
            raise ValueError("Repository không được là None.")
        if strategy is None:
            raise ValueError("Strategy không được là None.")

        self._repository: IRepository[T] = repository
        self._strategy: ISelectionStrategy[T] = strategy

    @property
    def strategy(self) -> ISelectionStrategy[T]:
        return self._strategy

    def change_strategy(self, new_strategy: ISelectionStrategy[T]) -> None:
        if new_strategy is None:
            raise ValueError("Chiến lược mới không được là None.")
        self._strategy = new_strategy

    def allocate(self, additional_condition: Optional[Callable[[T], bool]] = None) -> T:
        # 1. Lấy tất cả đối tượng từ kho
        all_items: List[T] = self._repository.get_all()

        # 2. Lọc thiết bị sẵn sàng sử dụng
        ready_candidates: List[T] = [item for item in all_items if item.is_ready_for_use()]

        # 3. Áp dụng điều kiện bổ sung nếu có
        if additional_condition is not None:
            filtered_candidates: List[T] = [item for item in ready_candidates if additional_condition(item)]
        else:
            filtered_candidates = ready_candidates

        # Kiểm tra danh sách ứng viên trước khi chọn
        if not filtered_candidates:
            raise NoSuitableItemException("Không có thiết bị nào sẵn sàng và thỏa mãn điều kiện yêu cầu.")

        # 4. Sử dụng chiến lược hiện tại để chọn thiết bị
        selected_device: T = self._strategy.select(filtered_candidates)

        # 5. Đánh dấu mượn thiết bị
        selected_device.borrow()

        # 6. Trả về thiết bị đã cấp phát
        return selected_device
