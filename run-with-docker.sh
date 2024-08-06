#!/bin/bash

docker build --platform linux/amd64 -t housing-scrapper . && \
    docker run --platform linux/amd64 -it --env-file .env housing-scrapper "$@" #&& \
    #docker rmi $(docker images -q housing-scrapper)
