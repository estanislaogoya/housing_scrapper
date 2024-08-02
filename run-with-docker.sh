#!/bin/bash

docker build -t housing-scrapper . && \
    docker run --rm --env-file .env housing-scrapper "$@" && \
    docker rmi $(docker images -q housing-scrapper)
