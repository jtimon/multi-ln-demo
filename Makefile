# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

.PHONY: docker-demo-regtest docker-demo-2-chains docker-rust-2-chains docker-run-3-chains
all: docker-demo-2-chains

docker-demo-regtest:
	export PYDEMO_CHAINS=regtest ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale db=0 \
	--scale bob_gateway=0 \
	--scale bitcoind_chain_2=0 \
	--scale bitcoind_chain_3=0 \
	--scale clightning_bob_chain_2=0 \
	--scale clightning_carol_chain_2=0 \
	--scale clightning_carol_chain_3=0 \
	--scale clightning_david_chain_3=0 \

docker-demo-2-chains:
	export PYDEMO_CHAINS=regtest,chain_2 ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale bitcoind_chain_3=0 \
	--scale clightning_carol_chain_3=0 \
	--scale clightning_david_chain_3=0 \

docker-demo-3-chains:
	export PYDEMO_CHAINS=regtest,chain_2,chain_3 ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \

docker-rust-2-chains:
	cd docker/rustdemo-2-chains && docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit

# TODO fix this: $() isn't working properly
docker-clean-containers:
	docker stop $(docker ps -aq) ; docker rm $(docker ps -aq)
