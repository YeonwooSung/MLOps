naive-server:
	docker-compose -p naive -f naive-docker-compose.yaml up -d

naive-clean:
	docker-compose -p naive -f naive-docker-compose.yaml down -v

kafka-server:
	docker-compose -p kafka -f kafka-docker-compose.yaml up -d

kafka-server-clean:
	docker-compose -p kafka -f kafka-docker-compose.yaml down -v
	docker rmi -f \
		kafka-connect \
		confluentinc/cp-zookeeper:7.3.0 \
		confluentinc/cp-kafka:7.3.0 \
		confluentinc/cp-spartema-registry:7.3.0

target-server:
	docker-compose -p target -f target-docker-compose.yaml up -d

target-server-clean:
	docker-compose -p target -f target-docker-compose.yaml down -v
	docker rmi -f target-table-creator

source-connector:
	curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @source_connector.json

sink-connector:
	curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @sink_connector.json

server:
	make kafka-server
	make target-server
	sleep 60
	make source-connector
	make sink-connector

server-clean:
	make target-server-clean
	make kafka-server-clean

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

target-db-connection:
	PGPASSWORD=targetpassword psql -h localhost -p 5433 -U targetuser -d targetdatabase
