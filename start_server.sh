#!/bin/sh

if [ "$1" = "dev" ]
then
  python manage.py runserver 0.0.0.0:80
else
  killall gunicorn
  gunicorn volky_server.wsgi:application --bind=127.0.0.1:8001 --preload &

  service nginx restart
fi
