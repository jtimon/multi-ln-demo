# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

DOCKER_IMAGE=multilndemo

.PHONY: docker-build docker-run
all: docker-run

docker-build:
	docker build --tag=${DOCKER_IMAGE} .

docker-run: docker-build
	docker run ${DOCKER_IMAGE}
