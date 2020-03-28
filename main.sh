#!/usr/bin/env zsh

package=talk_to_me

if [ ! -d env/ ]
then
    python3 -m virtualenv env/
	. ./env/bin/activate
	pip3 install \
		 -r dev-requirements.txt \
		 -r requirements.txt
fi

. ./env/bin/activate
set -e -x

MYPYPATH=./stubs \
		dmypy run -- \
		--follow-imports=error \
		--ignore-missing-imports \
		--strict \
		-p ${package}

# python3 -m pylint

# python3 -m pytest -v

if command -v scc
then
	scc ${package}
fi

python3 main.py './facebook-charmoniumq.zip' 'Sam Grayson'
