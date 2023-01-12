DOCKER_REPOSITORY ?= docker-registry.homelab.jph.dev
DOCKER_IMAGE_NAME ?= appaemon
GIT_HASH ?= $(shell git rev-parse --short HEAD)

build:
	docker build -t ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:${GIT_HASH} .

tag:
	docker tag  ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:${GIT_HASH} ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:latest

push:
	docker push ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:${GIT_HASH}

release: tag
	docker pull ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:${GIT_HASH}
	docker push ${DOCKER_REPOSITORY}/${DOCKER_IMAGE_NAME}:latest
