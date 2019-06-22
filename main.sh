#!/usr/bin/env zsh

package=talk_to_me

if [ ! -d env/ ]
then
    python3 -m virtualenv env/
fi

. ./env/bin/activate

set -e -x

pip3 install -r dev-requirements.txt -r requirements.txt

python3 -m mypy --ignore-missing-imports --strict -p ${package}

# python3 -m pylint

# python3 -m pytest -v

scc ${package}

python3 main.py
