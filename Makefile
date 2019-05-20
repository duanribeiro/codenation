loans = 50
clients = 10

generateloans:
	python ./project_helpers/generate_data/main.py --loans $(loans) --clients $(clients) $(shell pwd) && python ./codenation/manage.py loaddata $(shell pwd)/test_data.json && rm $(shell pwd)/test_data.json

dev:
	docker-compose build
	docker-compose up -d