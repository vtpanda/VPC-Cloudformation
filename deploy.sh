#!/bin/bash

if [ -e ./deploy-parameters.json ]
then
    python3 ./deploy.py "$(< ./deploy-parameters.json)"
else
    python3 ./deploy.py
fi
