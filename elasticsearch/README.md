# Elasticsearch

## Set up Elasticsearch with Docker

For more information, see the [official Elasticsearch Docker documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html).

```bash
# Create a network for the containers
docker network create elastic

# Pull the Elasticsearch image
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.15.3

# Start the Elasticsearch container
# Use the -m flag to set a memory limit for the container.
# This removes the need to manually set the JVM size.
docker run --name es01 --net elastic -p 9200:9200 -it -m 1GB docker.elastic.co/elasticsearch/elasticsearch:8.15.3

# The command above prints the `elastic` password and token to the console (token is used for kibana, etc)

# Run Kibana
docker pull docker.elastic.co/kibana/kibana:8.15.3
docker run --name kib01 --net elastic -p 5601:5601 docker.elastic.co/kibana/kibana:8.15.3
```
