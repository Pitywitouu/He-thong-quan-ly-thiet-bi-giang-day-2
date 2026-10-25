from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar

T = TypeVar("T")


class ISelectionStrategy(Generic[T], ABC):
    @abstractmethod
    def select(self, candidates: Sequence[T]) -> T:
        raise NotImplementedError
