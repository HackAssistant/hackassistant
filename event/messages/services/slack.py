import logging

from slack import WebClient
from slack.errors import SlackApiError

from event.messages.services.base import ServiceAbstract
from user.models import User


class SlackMessageService(ServiceAbstract):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.announcement_channel = kwargs.get('ANNOUNCEMENT_CHANNEL', None)
        token = kwargs.get('ACCESS_TOKEN', None)
        if token is None:
            self.client = None
            self.logger.error('Slack token missing')
        else:
            self.client = WebClient(token=token)

    def send_message(self, message: str, user: User) -> bool:
        if self.client is None:
            return False
        try:
            response = self.client.users_lookupByEmail(email=user.email)
            if not response.data['ok']:
                self.logger.error('Could not find any slack user with email %s' % user.email)
                return False
            identifier = response.data['user']['id']
            response = self.client.conversations_open(users=identifier)
            if not response.data['ok']:
                self.logger.error('Could not open any conversation with the user with id %s' % identifier)
                return False
            channel = response.data['channel']['id']
            self.client.chat_postMessage(channel=channel, text=message)
        except SlackApiError as e:
            self.logger.error(e)
            return False

    def make_announcement(self, message: str) -> bool:
        if self.client is None:
            raise self.ServiceException('Slack token missing')
        try:
            self.client.chat_postMessage(channel=self.announcement_channel, text=message)
            return True
        except SlackApiError as e:
            self.logger.error(e)
            raise self.ServiceException(e)
