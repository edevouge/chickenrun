NAME ?= $(shell basename $(PWD))
VERSION := $(shell cat .VERSION)
HASH :=  $(shell git rev-parse --short HEAD)

REGISTRY ?= edevouge
DOCKER_ROOT := ./


all: build tag push

.PHONY: build-docker
build:
	docker build $(CUSTOM_BUILD_ARGS) -t $(NAME):$(VERSION)-$(HASH) $(DOCKER_ROOT)

.PHONY: build-docker-nc
build-nc:
	docker build $(CUSTOM_BUILD_ARGS) --no-cache -t $(NAME):$(VERSION)-$(HASH) $(DOCKER_ROOT)

.PHONY: tag
tag:
	docker tag $(NAME):$(VERSION)-$(HASH) $(REGISTRY)/$(NAME):$(VERSION)-$(HASH)
	docker tag $(NAME):$(VERSION)-$(HASH) $(NAME):latest
	docker tag $(NAME):$(VERSION)-$(HASH) $(REGISTRY)/$(NAME):latest

.PHONY: push
push:
	docker push $(REGISTRY)/$(NAME):$(VERSION)-$(HASH)
	docker push $(REGISTRY)/$(NAME):latest
