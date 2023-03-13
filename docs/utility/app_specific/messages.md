# MessageServiceManager [+](/event/messages/services/manager.py)

This is a utility class to send messages (slack or/and more to be added) to the channels or users.
This can be used to inform about some state about something to the users at the hackathon.

## Requirements

Set up MESSAGES_SERVICES for each service you want to use for your hackathon.

## Send message to user

- Import and call the constructor of the `MessageServiceManager` singleton
- Call the `send_message_to_user` with the following parameters:

  - **message (str)**: Message text to send to the user.
  - **user**: User instance from [django User model app](/user/models.py) of the user wanted to send a message to.
  - **sent_to_services** [Optional]: List of services names where you want to send the message. If not passed as argument it will be sent to all services.

```python
from event.messages.services import MessageServiceManager
from user.models import User

def some_view_or_another_method(request):
    manager = MessageServiceManager()
    user = User.objects.get(id=1) or request.user
    
    # Message only sent to Slack
    manager.send_message_to_user(message='Test', user=user, sent_to_services=['SlackMessageService'])
    
    # Message sent to all services
    manager.send_message_to_user(message='Test', user=user)
```

## Send message to announcement channel

- Import and call the constructor of the `MessageServiceManager` singleton
- Call the `make_announcement` with the following parameters:

  - **message (str)**: Message text to send to the user.
  - **sent_to_services** [Optional]: List of services names where you want to send the message. If not passed as argument it will be sent to all services.
  - **error_callback** [Optional]: Function if the service throws an exception (the function will be executed asynchronous).

```python
from event.messages.services import MessageServiceManager

manager = MessageServiceManager()

# Announcement only sent to all services
manager.make_announcement(message='Announcement')

# Announcement only sent to Slack
manager.make_announcement(message='Announcement', sent_to_services=['SlackMessageService'])

# Announcement only sent to Slack with a change to a model if throws error
some_instance_from_a_model = None
some_instance_from_a_model.status = 'Good'
some_instance_from_a_model.save()

# Create error_callback on the go to save the instance location in memory
def error_callback(e):
  some_instance_from_a_model.error = str(e)
  some_instance_from_a_model.status = 'Error'
  some_instance_from_a_model.save()

manager.make_announcement(message='Announcement', sent_to_services=['SlackMessageService'], error_callback=error_callback)
```

## Create new service for messaging

We all know that Slack is the main service provided to communicate in a hackathon, but we are happy to integrate other 
new technologies as Discord or others. That's why you can easily create a new ServiceManager creating a class that 
inherits the [`ServiceAbstract`](/event/messages/services/base.py). Then you will need to override the abstract methods:
`send_message` and `make_announcement`. We might integrate Discord soon.
