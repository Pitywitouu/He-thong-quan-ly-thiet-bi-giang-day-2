from __future__ import annotations
from typing import Callable, Generic, Sequence, TypeVar

from strategies.selection_strategy import ISelectionStrategy
from exceptions.device_exceptions import NoSuitableItemException

T = TypeVar("T")


class HighestPriorityStrategy(Generic[T], ISelectionStrategy[T]):
    def __init__(self, score_selector: Callable[[T], float]) -> None:
        if not callable(score_selector):
            raise ValueError("score_selector phải là một hàm (callable) tính điểm từ đối tượng.")
        self._score_selector: Callable[[T], float] = score_selector

    def select(self, candidates: Sequence[T]) -> T:
        if not candidates:
            raise NoSuitableItemException("Danh sách ứng viên rỗng, không thể chọn đối tượng có điểm cao nhất.")

        return max(candidates, key=self._score_selector)

    def __repr__(self) -> str:
        return f"HighestPriorityStrategy(score_selector={self._score_selector.__name__ if hasattr(self._score_selector, '__name__') else '<lambda>'})"
