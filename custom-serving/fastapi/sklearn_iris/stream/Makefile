stream-server:
	docker-compose -p stream -f stream-docker-compose.yaml up -d

dashboard-server:
	docker-compose -p dashboard -f grafana-docker-compose.yaml up -d

stream-server-clean:
	docker-compose -p stream -f stream-docker-compose.yaml down -v
	docker rmi -f stream-data-subscriber

dashboard-server-clean:
	docker-compose -p dashboard -f grafana-docker-compose.yaml down -v
	docker rmi -f grafana/grafana

server:
	make stream-server
	make dashboard-server

server-clean:
	make stream-server-clean
	make dashboard-server-clean

dependency:
	#make -C ../db_setup/ server
	make -C ../model_deployment/ all
	make -C ../kafka/ server

dependency-clean:
	make -C ../kafka/ server-clean
	make -C ../model_deployment/ server-clean
	make -C ../db_setup/ server-clean

all:
	make dependency
	make server

all-clean:
	make server-clean
	make dependency-clean

target-db-connection:
	PGPASSWORD=targetpassword psql -h localhost -p 5433 -U targetuser -d targetdatabase
