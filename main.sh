#!/usr/bin/env zsh

package=talk_to_me

. ./env/bin/activate

set +e

# pip3 install -r dev-requirements.txt -r requirements.txt

# python -m spacy download en_core_web_lg

python3 -m mypy --ignore-missing-imports --strict -p ${package}

# python3 -m pytest -v

scc ${package}

python3 main.py
