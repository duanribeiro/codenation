loans = 50

generateloans:
	python ./project_helpers/generate_data/main.py --loans $(loans) $(shell pwd) && python ./codenation/manage.py loaddata $(shell pwd)/test_data.json && rm $(shell pwd)/test_data.json

dev:
	docker-compose build
	docker-compose up -d