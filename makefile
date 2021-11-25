test:
	pytest

venv:
	python3 -m venv test
	source test/bin/activate
	pip3 install --upgrade pip

requirements:
	pip3 install -r requirements.txt
