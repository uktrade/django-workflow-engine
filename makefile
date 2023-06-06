setup:
	poetry install --with=testing,utils,docs

test:
	poetry run pytest $(test)

venv:
	python3 -m venv test
	source test/bin/activate
	pip3 install --upgrade pip

requirements:
	pip3 install -r requirements.txt

build-package:
	poetry build

push-pypi-test:
	poetry publish -r test-pypi

push-pypi:
	poetry publish

serve-docs:
	poetry run mkdocs serve -a localhost:8001
