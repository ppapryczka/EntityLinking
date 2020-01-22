#!/usr/bin/env bash

docker run \
  --rm \
  --name entity_linking_redis \
  -p "6379:6379" \
  -d redis