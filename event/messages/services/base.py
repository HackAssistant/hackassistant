from abc import ABC, abstractmethod

from user.models import User


class ServiceAbstract(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def send_message(self, message: str, user: User) -> bool:
        return False

    @abstractmethod
    def make_announcement(self, message: str) -> bool:
        return False
