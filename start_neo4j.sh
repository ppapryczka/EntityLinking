#!/usr/bin/env bash

docker run --rm --name entity_linking_neo4j -p "7687:7687" -d --env NEO4J_AUTH=neo4j/test neo4j:latest
