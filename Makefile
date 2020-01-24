# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

.PHONY: docker-demo-regtest docker-demo-2-chains docker-rust-2-chains docker-run-3-chains
all: docker-demo-2-chains

pydemo-regtest:
	export PYDEMO_CHAINS=regtest ; \
	export LIGHTNINGD_PROCFILE=/wd/docker/regtest/lightningd.Procfile ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale bitcoind_chain_2=0 \
	--scale bitcoind_chain_3=0 \
	--scale bob_gateway=0 \
	--scale db=0 \

pydemo-2-chains:
	export PYDEMO_CHAINS=regtest,chain_2 ; \
	export LIGHTNINGD_PROCFILE=/wd/docker/2-chains/lightningd.Procfile ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale bitcoind_chain_3=0 \

pydemo-3-chains:
	export PYDEMO_CHAINS=regtest,chain_2,chain_3 ; \
	export LIGHTNINGD_PROCFILE=/wd/docker/3-chains/lightningd.Procfile ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \

rsdemo-2-chains:
	cd docker/rustdemo-2-chains && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit

# TODO fix this: $() isn't working properly
docker-clean-containers:
	docker stop $(docker ps -aq) ; docker rm $(docker ps -aq)
