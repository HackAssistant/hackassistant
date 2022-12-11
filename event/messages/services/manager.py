from multiprocessing import Pool

from django.conf import settings

from app.patterns import SingletonMeta
from event.messages import services
from event.messages.services.base import ServiceAbstract
from user.models import User


class MessageServiceManager(metaclass=SingletonMeta):
    class MessageServiceDoNotExists(Exception):
        pass

    def __init__(self) -> None:
        super().__init__()
        self.services = self.__get_services()

    @classmethod
    def get_services_names(cls, only_names=True):
        services_conf = getattr(settings, 'MESSAGES_SERVICES', {})
        if not isinstance(services_conf, dict):
            raise cls.MessageServiceDoNotExists('MESSAGES_SERVICES expected a dict and %s was found' %
                                                type(services_conf))
        return services_conf.keys() if only_names else services_conf

    def __get_services(self) -> dict:
        result = {}
        services_conf = self.get_services_names(only_names=False)
        for service_name, service_conf in services_conf.items():
            service = getattr(services, service_name, None)
            if service is None or not issubclass(service, ServiceAbstract):
                raise self.MessageServiceDoNotExists('The service %s do not exists' % service_name)
            result[service_name] = service(**service_conf)
        return result

    def send_message_to_user(self, message: str, user: User, sent_to_services=None):
        if sent_to_services is not None and not isinstance(sent_to_services, list) \
                and not isinstance(sent_to_services, tuple):
            raise self.MessageServiceDoNotExists('sent_to_services must be list, tuple or None and %s was found' %
                                                 type(sent_to_services))
        for service_name, service in self.services.items():
            if sent_to_services is None or service_name in sent_to_services:
                pool = Pool(processes=1)
                pool.apply_async(service.send_message, kwds={'message': message, 'user': user})

    def make_announcement(self, message: str, sent_to_services=None):
        if sent_to_services is not None and not isinstance(sent_to_services, list) \
                and not isinstance(sent_to_services, tuple):
            raise self.MessageServiceDoNotExists('sent_to_services must be list, tuple or None and %s was found' %
                                                 type(sent_to_services))
        for service_name, service in self.services.items():
            if sent_to_services is None or service_name in sent_to_services:
                pool = Pool(processes=1)
                pool.apply_async(service.make_announcement, kwds={'message': message})
