# Friends app [+](/friends/.)

This optional app enables the participants to apply with their friends and then for the organizers to group their applications 
in order to invite all the friends.

## Features

- Apply with friends for all the roles of the hackathon (User required).
- Invite with a group by friends group that shows how many of them are already invited.
- Limitation of friends group configurable.
- Team closed when one of their team is invited.

## Configuration

- **App**: The whole app is optional and can be removed of `INSTALLED_APPS` on [`settings.py`](/app/settings.py) 
if it is not wanted.
- **Friends limits**: You can set the limit of friends that the participants can add to their group.
Set the limit on [`hackathon_variables.py`](/app/hackathon_variables.py) with the variable `FRIENDS_MAX_CAPACITY`.
Set this to `None` if you don't want any limit.

## Future ideas

- Separate the friends groups by the role of the participants.
