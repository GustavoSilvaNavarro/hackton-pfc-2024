#!make
PORT = 8000
SERVICE_NAME = expense_tracker_api
CONTAINER_NAME = $(SERVICE_NAME)
DOCKER_COMPOSE_TAG = $(SERVICE_NAME)_1
PYFILES=app/*.py tests/*/*.py
# PYFILES=app/*.py

KUSTOMIZE_VERSION := $(shell test -e /usr/local/bin/kustomize && /usr/local/bin/kustomize version | cut -f2 -d/ | cut -f1 -d' ')
KUBEVAL_VERSION := $(shell test -e /usr/local/bin/kubeval && /usr/local/bin/kubeval --version | grep Version | cut -f2 -d' ')

# Virtual env
venv:
	python -m venv .venv

activate-venv:
	source .venv/bin/activate

# Install
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements_dev.txt

# Run
dev:
	uvicorn app:app --reload --proxy-headers --host 0.0.0.0 --port 8000

start: upgrade
	uvicorn app:app --proxy-headers --host 0.0.0.0 --port 8000

# dev: install-internal upgrade
# 	uvicorn app:app --reload --proxy-headers --host 0.0.0.0 --port 8000

# start: install-internal upgrade
# 	uvicorn app:app --proxy-headers --host 0.0.0.0 --port 8000


# DB
# Sync Migrations
setup-alembic:
	alembic init migrations

# Async Migrations
async-alembic:
	alembic init -t async migrations

migrate:
	set -a; . ./dev.env; alembic revision --autogenerate -m "$(filename)"

upgrade:
	set -a; . ./dev.env; alembic upgrade head

downgrade:
	set -a; . ./dev.env; alembic downgrade $(version)

head:
	set -a; . ./dev.env; alembic current

seed-local-db:
	PYTHONPATH=/Users/gustavosilvanavarro/workspace/gustavo-silva/full-stack-projects/trips-tracker python seeds/seed.py

# Local Testing
local-db:
	docker run -d --name ts_db -p 5432:5432 -e POSTGRES_PASSWORD=password123 -e POSTGRES_USER=postgres \
	-e POSTGRES_DB=expense-tracker timescale/timescaledb:latest-pg16

test-db:
	docker run -d --name ts_test_db -p 5432:5432 -e POSTGRES_PASSWORD=password123 -e POSTGRES_USER=postgres \
  -e POSTGRES_DB=test_expense-tracker timescale/timescaledb:latest-pg16

# Tests Unit and Integration
run-tests:
	pytest -v

run-unit:
	pytest tests/unit -v

run-integration:
	pytest tests/integration -v

integration-tests:
	./wait-for.sh http://expenser-api:8000/expense-tracker/healthz pytest -vv tests/integration --capture=tee-sys --asyncio-mode=auto

# Pipeline commands
setup:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements_dev.txt

unit:
	set -a; . ./dev.env; pytest -vv tests/unit/

integration: down up-integration
	docker-compose -f ./docker-compose.yml up --exit-code-from integration_tests integration_tests

lint:
	pydocstyle $(PYFILES)
	pycodestyle $(PYFILES)
	pylint $(PYFILES)

format:
	black ${PYFILES}
	isort ${PYFILES}

check:
	black --check ${PYFILES}
	isort --check ${PYFILES}

scan:
	bandit -r . -lll  # Show 3 lines of context
	safety check

commitready: format unit integration
	@echo 'Commit ready'

# Docker commands
build-base:
	DOCKER_BUILDKIT=1 docker build -f Dockerfile.base -t $(SERVICE_NAME)_base .

run-external-services:
	docker compose -f ./docker-compose.inf.yml up -d db

up: build-base
	docker-compose -f ./docker-compose.yml -f ./docker-compose.inf.yml build
	docker-compose -f ./docker-compose.yml -f ./docker-compose.inf.yml up -d --force-recreate --scale integration_tests=0

up-integration: build-base
	docker-compose -f ./docker-compose.yml -f ./docker-compose.inf.yml up --force-recreate

down:
	docker-compose -f ./docker-compose.yml -f ./docker-compose.inf.yml down --remove-orphans

down-rm:
	docker compose -f ./docker-compose.yml -f ./docker-compose.inf.yml down --remove-orphans --rmi all

# downup: down up

dev-up:
	docker-compose -f ./docker-compose.inf.yml -f ./docker-compose.inf.yml -f ./docker-compose.dev.yml build
	docker-compose -f ./docker-compose.inf.yml -f ./docker-compose.dev.yml up -d --force-recreate

# dev-down:
# 	docker-compose -f ./docker-compose.inf.yml -f ./docker-compose.dev.yml down --remove-orphans

# rebuild:
# 	docker-compose up --build --force-recreate --no-deps $(SERVICE_NAME)

# run: rebuild
# 	docker run  -p $(PORT):$(PORT) --name $(DOCKER_COMPOSE_TAG) -it $(DOCKER_COMPOSE_TAG) /bin/sh

# exec-shell:
# 	docker exec -it $(DOCKER_COMPOSE_TAG) /bin/bash

# docker-build:
# 	docker build -t $(SERVICE_NAME) .

# docker-run: docker-build
# 	docker run  -p $(PORT):$(PORT) --name $(SERVICE_NAME) -it $(SERVICE_NAME)

# docker-exec-shell:
# 	docker exec -it $(SERVICE_NAME) /bin/bash

# Manifest Validators
# validate_manifest:
# 	rm -f .manifest
# 	kustomize build .deploy/$(TARGET_ENVIRONMENT) >> .manifest
# 	[ -s .manifest ] || (echo "Manifest is Empty" ; exit 2)
# 	kubeval .manifest --kubernetes-version 1.18.0 --ignore-missing-schemas
# 	echo "Manifest Validated"
# 	rm -rf .manifest

# validate_manifest_if_changed:
# 	if test -n "$(shell git ls-files -m .deploy/)"; \
# 		then make validate_manifest; \
# 		else echo deploy/ files unchanged; \
# 	fi

# install_validate_manifest:
# ifneq ($(KUSTOMIZE_VERSION), v3.8.1)
# 	curl -o kustomize.tar.gz --location https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize/v3.8.1/kustomize_v3.8.1_linux_amd64.tar.gz
# 	tar -xzvf kustomize.tar.gz kustomize
# 	chmod u+x kustomize
# 	sudo mv kustomize /usr/local/bin/
# 	rm kustomize.tar.gz
# endif
# ifneq ($(KUBEVAL_VERSION), 0.15.0)
# 	wget -O kubeval-linux-amd64.tar.gz https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz
# 	tar xf kubeval-linux-amd64.tar.gz kubeval
# 	chmod u+x kubeval
# 	sudo mv kubeval /usr/local/bin/
# 	rm kubeval-linux-amd64.tar.gz
# endif