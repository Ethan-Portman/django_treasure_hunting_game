#!/usr/bin/env bash

pipenv run pipenv install
python ics226/manage.py collectstatic --no-input
python ics226/manage.py migrate
