FROM python:3.9.13
RUN apt-get update
RUN apt-get install -y cron && touch /var/log/cron.log
RUN pip install --upgrade pip
WORKDIR /code

COPY requirements.txt /code/
RUN pip3 install -r requirements.txt && pip install gunicorn

COPY . /code/

CMD ["sh", "./run.sh"]
