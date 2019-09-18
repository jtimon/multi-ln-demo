# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

DOCKER_IMAGE=multilndemo

.PHONY: docker-build docker-run-regtest docker-run-2-chains
all: docker-run-regtest docker-run-2-chains

docker-build:
	docker build --tag=${DOCKER_IMAGE} .

docker-run-regtest: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/regtest-entry-point.sh"

docker-run-2-chains: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/2-chains-entry-point.sh"
