#!/bin/sh
python manage.py makemigrations WebConsole
python manage.py migrate WebConsole
python manage.py makemigrations sessions
python manage.py migrate sessions
python manage.py makemigrations admin
python manage.py migrate admin
python manage.py makemigrations contenttypes
python manage.py migrate contenttypes
