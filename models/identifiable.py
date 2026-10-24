from abc import ABC, abstractmethod


class IIdentifiable(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        raise NotImplementedError
