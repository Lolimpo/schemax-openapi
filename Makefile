PROJECT_NAME=schemax-openapi

.PHONY: install
install:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet -r requirements.txt -r requirements-dev.txt

.PHONY: build
build:
	pip3 install --quiet --upgrade pip
	pip3 install --quiet --upgrade setuptools wheel twine
	python3 setup.py sdist bdist_wheel

.PHONY: publish
publish:
	twine upload dist/*

.PHONY: check-types
check-types:
	python3 -m mypy ${PROJECT_NAME} --strict

.PHONY: check-imports
check-imports:
	python3 -m isort ${PROJECT_NAME} --check-only

.PHONY: sort-imports
sort-imports:
	python3 -m isort ${PROJECT_NAME}

.PHONY: check-style
check-style:
	python3 -m flake8 ${PROJECT_NAME}

.PHONY: lint
lint: check-types check-style check-imports
