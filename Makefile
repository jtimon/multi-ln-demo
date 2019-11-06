# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

DOCKER_IMAGE=multilndemo

.PHONY: docker-build docker-demo-regtest docker-demo-2-chains docker-rust-2-chains docker-run-5-chains
all: docker-demo-2-chains

docker-build:
	docker build --tag=${DOCKER_IMAGE} .

docker-demo-regtest: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/regtest-entry-point.sh"

docker-demo-2-chains: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/2-chains-entry-point.sh"

docker-demo-5-chains: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/5-chains-entry-point.sh"

docker-rust-2-chains: docker-build
	docker run ${DOCKER_IMAGE} bash -c "bash /wd/rustdemo-2-chains-entry-point.sh"
