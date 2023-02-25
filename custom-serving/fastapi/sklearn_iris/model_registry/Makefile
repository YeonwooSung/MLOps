init:
	pip install -U pip
	pip install boto3==1.26.8 mlflow==1.30.0 scikit-learn pandas psycopg2-binary

save_model:
	make init
	python3 save_model_to_registry.py
	ls

server:
	docker-compose up -d

server-clean:
	docker-compose down -v
	docker rmi -f mlflow-server minio/minio

dependency:
	make -C ../db_setup/ server

dependency-clean:
	make -C ../db_setup/ server-clean

all:
	make dependency
	make server

all-clean:
	make server-clean
	make dependency-clean
