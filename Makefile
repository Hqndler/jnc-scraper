all:
	docker compose -f docker-compose.yml up -d --build

down:
	docker compose -f docker-compose.yml down

clean: down
	docker rmi -f jncscrapper

re:	clean all

.PHONY:	all down clean re
