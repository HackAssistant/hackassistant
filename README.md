<br>
<p align="center">
  <img alt="HackAssistant" src="https://avatars2.githubusercontent.com/u/33712329?s=200&v=4" width="200"/>
</p>
<br>

📝 Hackathon registration server. Remake of the [HackAssistant/registration](https://github.com/HackAssistant/registration) in order to improve the future development and maintainability. 

## Features

- Email sign up ✉️
- Email verification 📨
- Forgot password 🤔
- Ip block on failed login tries & ip blocklist ✋ (Optional)
- Dark mode 🌚 🌝 Light mode (Optional)

## Documentation

There's a really extended documentation for configurations or development of the application [here](/docs/README.md).

## Development

The development if this Django app can be made by Python or Docker-Compose. 
We recommend the use of Docker.

## Docker-Compose

Needs: Docker, Docker-Compose

- `./install.sh` (Creates virtualenviroment, install requirements.txt and migrates DB)
- `docker-compose up` (Starts server)

That is all! 😃 If you need to run any python command just do as the following examples:

- Install new library: `docker-compose run python -m pip install [library]`
- Make migrations: `docker-compose run python manage.py makemigrations`
- Migrate: `docker-compose run python manage.py migrate`

### Python

Needs: Python 3.X, virtualenv

- `git clone git@github.com:HackAssistant/hackassistant.git && cd hackassistant`
- `virtualenv env --python=python3`
- `source ./env/bin/activate`
- `pip install -r requirements.txt`
- `python manage.py migrate`
- `python manage.py createsuperuser` (creates superuser to manage all the app)
- `python manage.py runserver`
