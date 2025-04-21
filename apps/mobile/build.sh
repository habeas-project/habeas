#!/bin/bash


docker build . -t habmobiletest
docker run --rm -it --entrypoint bash habmobiletest
