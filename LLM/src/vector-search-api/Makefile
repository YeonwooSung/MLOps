IMAGE_NAME=vector-search

download:
	kaggle datasets download \
	-d joelpl/news-portal-recommendations-npr-by-globo \
	-p ./data

	unzip ./data/news-portal-recommendations-npr-by-globo.zip -d ./data

run:
	python3 -m flask run --host=0.0.0.0 --debug --port=3000

index:
	python -m scripts.reindex

qdrant-terminal:
	docker exec \
	-it \
	$(IMAGE_NAME) \
	/bin/bash

qdrant-server:
	docker run \
	-p 6333:6333 \
	-p 6334:6334 \
    -v $(PWD)/qdrant_data:/qdrant/storage:z \
	--name $(IMAGE_NAME) \
    qdrant/qdrant

# port-usage:
# 	lsof -i tcp:${PORT}

docker-clean:
	# docker system prune -a
	docker ps -a  | awk '{print $$1}' | tail -n +2 | xargs docker rm -f
	docker image list -a | awk '{print $$3}' | tail -n+2 | xargs docker image rm -f
