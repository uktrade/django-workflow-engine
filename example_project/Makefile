SHELL := /bin/bash

manage = poetry run python manage.py

build:
	poetry install

init:
	$(manage) loaddata fixtures/test_users.json

run:
	./scripts/run.sh

shell:
	$(manage) shell

superuser:
	$(manage) createsuperuser
