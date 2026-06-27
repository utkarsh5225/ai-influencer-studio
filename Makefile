.PHONY: build up down logs deploy

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

deploy: build up
	@echo "Deployed successfully on RunPod!"
