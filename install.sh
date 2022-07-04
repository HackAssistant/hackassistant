if [ ! -z "$1" ]; then
  pip install virtualenv
  virtualenv env --python=python3
else
  DIR="./env"
  if [ ! -d "$DIR" ]; then
    docker-compose run --entrypoint sh python ./install.sh docker
  fi
  docker-compose run python -m pip install -r requirements.txt
  docker-compose run python manage.py migrate
  docker-compose rm -f
fi
