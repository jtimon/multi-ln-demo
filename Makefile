# Only use these programs directly or explain yourself:
#  awk cat cmp cp diff echo egrep expr false grep install-info ln ls
#  mkdir mv printf pwd rm rmdir sed sleep sort tar test touch tr true

.PHONY: docker-demo-regtest docker-demo-2-chains docker-rust-2-chains docker-run-5-chains
all: docker-demo-2-chains

docker-demo-regtest:
	cd docker/regtest && docker-compose up --build --force-recreate

docker-demo-2-chains:
	cd docker/2-chains && docker-compose up --build --force-recreate

docker-demo-5-chains:
	cd docker/5-chains && docker-compose up --build --force-recreate

docker-rust-2-chains:
	cd docker/rustdemo-2-chains && docker-compose up --build --force-recreate
