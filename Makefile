# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

.PHONY: pydemo-0-hop pydemo-1-hop pydemo-2-hop rsdemo-1-hop docker-clean-containers
all: pydemo-2-hop

pydemo-0-hop:
	export PYDEMO_HOPS=0 ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale rsdemo=0 \
	--scale db_bob=0 \
	--scale bob_gateway=0 \
	--scale db_carol=0 \
	--scale carol_gateway=0 \
	--scale elementsd_liquid_regtest=0 \
	--scale clightning_bob_liquid_regtest=0 \
	--scale clightning_carol_liquid_regtest=0 \

pydemo-1-hop:
	export PYDEMO_HOPS=1 ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale rsdemo=0 \
	--scale db_carol=0 \
	--scale carol_gateway=0 \

pydemo-2-hop:
	export PYDEMO_HOPS=2 ; \
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale rsdemo=0 \

rsdemo-1-hop:
	cd docker && docker-compose down -v && \
	docker-compose up --build --force-recreate -V --remove-orphans --abort-on-container-exit \
	--scale pydemo=0 \
	--scale db_carol=0 \
	--scale carol_gateway=0 \

docker-clean-containers:
	docker stop $$(docker ps -aq) ; docker rm $$(docker ps -aq)
