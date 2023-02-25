init:
	pip install -U pip
	pip install boto3==1.26.8 mlflow==1.30.0 "fastapi[all]" pandas scikit-learn

app:
	uvicorn app:app --reload

server:
	docker-compose up -d

server-clean:
	docker-compose down -v
	docker rmi -f api-with-model

dependency:
	make -C ../db_setup/ server
	sleep 100
	make -C ../model_registry/ server
	python ../model_registry/save_model_to_registry.py

dependency-clean:
	make -C ../model_registry/ server-clean
	make -C ../db_setup/ server-clean

all:
	make dependency
	make server

all-clean:
	make server-clean
	make dependency-clean
