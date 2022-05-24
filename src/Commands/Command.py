from abc import ABC, abstractmethod

class Command(ABC):
    @abstractmethod
    def __init__(self, args) -> None:
        pass

    @abstractmethod
    def execute(self, client) -> None:
        pass
