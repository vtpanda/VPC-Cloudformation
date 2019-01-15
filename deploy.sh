#!/bin/bash
cmd=$1

if [[ -z "$cmd" ]]; then
    cmd=none
fi

if [ -e ./deploy-parameters.json ]
then
    python3 ./deploy.py $cmd "$(< ./deploy-parameters.json)"
else
    echo "deploy-parameters.json not found"
fi
