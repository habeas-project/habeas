build:
	docker compose build

stop:
	docker compose down

run:
	docker compose up -d

query_postgres:
	psql -U postgres -h localhost -d habeas

generate_api_client:
	cd mobile;yarn generate-api
