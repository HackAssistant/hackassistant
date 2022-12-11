from event.messages.services.base import ServiceAbstract
from user.models import User


class FakeMessageService(ServiceAbstract):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def send_message(self, message: str, user: User) -> bool:
        print('Message to %s: %s' % (user, message))
        return True

    def make_announcement(self, message: str) -> bool:
        print('Announcement: %s' % message)
        return True
