from __future__ import annotations
from typing import Generic, Sequence, TypeVar

from strategies.selection_strategy import ISelectionStrategy
from exceptions.device_exceptions import NoSuitableItemException

T = TypeVar("T")


class FirstAvailableStrategy(Generic[T], ISelectionStrategy[T]):
    def select(self, candidates: Sequence[T]) -> T:
        if not candidates:
            raise NoSuitableItemException("Danh sách ứng viên rỗng, không thể chọn phần tử đầu tiên.")

        return candidates[0]

    def __repr__(self) -> str:
        return "FirstAvailableStrategy()"
