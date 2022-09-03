docker-compose run backend python manage.py collectstatic --noinput
docker-compose run backend python manage.py compress --force
docker-compose run backend python manage.py migrate
