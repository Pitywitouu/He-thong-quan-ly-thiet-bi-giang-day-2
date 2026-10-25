from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List, Optional, TypeVar

from models.identifiable import IIdentifiable
from exceptions.device_exceptions import DuplicateIdException

T = TypeVar("T", bound=IIdentifiable)


class IRepository(Generic[T], ABC):
    @abstractmethod
    def add(self, item: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove(self, id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, id: str) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def find_all(self, condition: Callable[[T], bool]) -> List[T]:
        raise NotImplementedError


class InMemoryRepository(Generic[T], IRepository[T]):
    def __init__(self) -> None:
        self._items: Dict[str, T] = {}

    def add(self, item: T) -> None:
        if item is None:
            raise ValueError("Không thể thêm phần tử None vào kho lưu trữ.")
        
        if not hasattr(item, "id") or not item.id:
            raise ValueError("Phần tử phải có thuộc tính 'id' hợp lệ.")

        if item.id in self._items:
            raise DuplicateIdException(item.id)

        self._items[item.id] = item

    def remove(self, id: str) -> bool:
        if not id:
            return False
        if id in self._items:
            del self._items[id]
            return True
        return False

    def find_by_id(self, id: str) -> Optional[T]:
        if not id:
            return None
        return self._items.get(id)

    def get_all(self) -> List[T]:
        return list(self._items.values())

    def find_all(self, condition: Callable[[T], bool]) -> List[T]:
        if condition is None:
            return self.get_all()
        return [item for item in self._items.values() if condition(item)]

    def __len__(self) -> int:
        return len(self._items)
