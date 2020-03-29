#!/usr/bin/env zsh

package=talk_to_me

if [ ! -d env/ ]
then
	python3 -m virtualenv env/
	. ./env/bin/activate
	pip3 install -r requirements.txt
fi

. ./env/bin/activate
set -e -x

python3 main.py './facebook-charmoniumq.zip' 'Sam Grayson'
