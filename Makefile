IMAGE_NAME ?= fit4110/iot-ingestion:lab04
CONTAINER_NAME ?= fit4110-iot-lab04
PORT ?= 8000

install:
	npm install

lint:
	npm run lint:openapi

mock:
	npm run mock:iot

test-mock:
	npm run test:mock

pytest:
	python -m pytest tests/ -v

pytest-verbose:
	python -m pytest tests/ -v -s

test-health:
	python -m pytest tests/test_health.py -v

test-functional:
	python -m pytest tests/test_functional.py -v

test-boss-fight-1:
	python -m pytest tests/test_boss_fight_1_boundary.py -v

test-boss-fight-2:
	python -m pytest tests/test_boss_fight_2_auth.py -v

test-boss-fight-3:
	python -m pytest tests/test_boss_fight_3_schema.py -v

test-integration:
	python -m pytest tests/test_integration.py -v

test-all:
	python -m pytest tests/ -v --tb=short

build:
	docker build -t $(IMAGE_NAME) .

run:
	docker run --rm --name $(CONTAINER_NAME) -p $(PORT):8000 --env-file .env.example $(IMAGE_NAME)

run-detached:
	docker run -d --rm --name $(CONTAINER_NAME) -p $(PORT):8000 --env-file .env.example $(IMAGE_NAME)

health:
	curl http://localhost:$(PORT)/health

test-docker:
	npm run test:local

stop:
	docker stop $(CONTAINER_NAME) || true

clean-reports:
	rm -f reports/*.xml reports/*.html reports/*.json
