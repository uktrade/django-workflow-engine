#!/bin/bash

set -ex

poetry run python manage.py migrate
poetry run python manage.py runserver
