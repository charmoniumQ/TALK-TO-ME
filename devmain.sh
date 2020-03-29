#!/usr/bin/env zsh

package=talk_to_me

if [ ! -d env/ ]
then
	# Ideally, I would run these things every time, but they take a
	# LONG time even when requirements are already satisfied.
	# Therefore, I only run them on fresh-install.
	python3 -m virtualenv env/
	. ./env/bin/activate
	pip3 install -r requirements.txt \
		 mypy mypy_extensions black pylint pytest pylint-exit
	if command -v go
	then
		go get -u github.com/boyter/scc/
	fi
fi

. ./env/bin/activate
set -e -x

if command -v scc
then
	scc .
fi

MYPYPATH=./stubs \
		dmypy run -- \
		--follow-imports=error \
		--ignore-missing-imports \
		--strict \
		-p ${package}

black --target-version py38 .
pylint talk_to_me stubs || pylint-exit -efail $?

python3 -m pytest -vv

./main.sh
