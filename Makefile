# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

.PHONY: docker-demo-regtest docker-demo-2-chains docker-rust-2-chains docker-run-3-chains
all: docker-demo-2-chains

docker-demo-regtest:
	export DEMO_ENTRYPOINT=/wd/docker/regtest/entrypoint.sh ; \
	export BITCOIND_ENTRYPOINT=/wd/docker/regtest/entrypoint-bitcoind.sh ; \
	cd docker && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit

docker-demo-2-chains:
	export DEMO_ENTRYPOINT=/wd/docker/2-chains/entrypoint.sh ; \
	export BITCOIND_ENTRYPOINT=/wd/docker/2-chains/entrypoint-bitcoind.sh ; \
	cd docker && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit

docker-demo-3-chains:
	export DEMO_ENTRYPOINT=/wd/docker/3-chains/entrypoint.sh ; \
	export BITCOIND_ENTRYPOINT=/wd/docker/3-chains/entrypoint-bitcoind.sh ; \
	cd docker && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit

docker-rust-2-chains:
	cd docker/rustdemo-2-chains && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit
