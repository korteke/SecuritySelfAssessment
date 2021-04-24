stop:
	docker-compose down

cleanup: stop
	docker system prune --force --volumes

webshell:
	docker run --rm -it ssa_web /bin/bash

build: stop
	docker-compose build

dbshell:
	docker run --rm -it mysql:5.7 /bin/bash

run:
	docker-compose down
	docker-compose up

default:
	echo choose a target, you ass
