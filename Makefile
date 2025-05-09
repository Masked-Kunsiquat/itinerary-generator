.PHONY: clean test lint install run-web run-dev build-docker

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf htmlcov .coverage build/ dist/ *.egg-info/

test:
	PYTHONPATH=. pytest \
		--cov=itinerary_generator \
		--cov-config=.coveragerc \
		--cov-report=term \
		--cov-report=html

lint:
	flake8 itinerary_generator tests

install:
	pip install -e .

run-web:
	python -m itinerary_generator.web

run-dev:
	FLASK_APP=itinerary_generator.web FLASK_DEBUG=1 python -m flask run --debug

build-docker:
	docker-compose build

docker-up:
	docker-compose up

docker-down:
	docker-compose down
