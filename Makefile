SHELL := /bin/bash
PWD := $(shell pwd)
PYTHON := python3
VENV := venv
SERVER_DIR := server
CLIENT_DIR := client

GIT_REMOTE = github.com/7574-sistemas-distribuidos/docker-compose-init

$(VENV)/bin/activate:
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip
	./$(VENV)/bin/pip install pytest

default: build

all:

deps:
	go mod tidy
	go mod vendor

build: deps
	GOOS=linux go build -o bin/client github.com/7574-sistemas-distribuidos/docker-compose-init/client
.PHONY: build

docker-image:
	docker build -f ./server/Dockerfile -t "server:latest" .
	docker build -f ./client/Dockerfile -t "client:latest" .
	# Execute this command from time to time to clean up intermediate stages generated 
	# during client build (your hard drive will like this :) ). Don't left uncommented if you 
	# want to avoid rebuilding client image every time the docker-compose-up command 
	# is executed, even when client code has not changed
	# docker rmi `docker images --filter label=intermediateStageToBeDeleted=true -q`
.PHONY: docker-image

docker-compose-up: docker-image
	docker compose -f docker-compose-dev.yaml up -d
.PHONY: docker-compose-up

docker-compose-down:
	docker compose -f docker-compose-dev.yaml stop -t 1
	docker compose -f docker-compose-dev.yaml down
.PHONY: docker-compose-down

docker-compose-logs:
	docker compose -f docker-compose-dev.yaml logs -f
.PHONY: docker-compose-logs

server-deps: $(VENV)/bin/activate
.PHONY: server-deps

test-server: server-deps
	PYTHONPATH=$(PWD)/$(SERVER_DIR) ./$(VENV)/bin/pytest $(SERVER_DIR)/tests
.PHONY: test-server

test-client:
	@docker run --rm \
		-v $(PWD):/build \
		-w /build/client/src \
		golang:1.17 /bin/bash -c "go test -v -mod=vendor ./... | sed ''/PASS/s//$$(printf "\033[32mPASS\033[0m")/'' | sed ''/FAIL/s//$$(printf "\033[31mFAIL\033[0m")/''"
.PHONY: test-client

test-healthcheck: docker-image
	./generar-compose.sh docker-compose-dev.yaml 3
	docker compose -f docker-compose-dev.yaml up server -d
	@echo "Esperando healthcheck..."
	@sleep 10
	docker inspect server | python3 -m json.tool | grep -A 10 '"Health"'
	docker compose -f docker-compose-dev.yaml down
.PHONY: test-healthcheck

clean-python:
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
.PHONY: clean-python