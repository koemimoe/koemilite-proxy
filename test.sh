#!/bin/bash

# this is a local helper script to run tests.
# this isn't available for gitlab-ci.yml for some reason, so i'll keep
# it here.

# ensure cache exists, tox and gitlab-ci.yml files are for other people
# and removing caches there don't really help.
mkdir -p cache
rm cache/*

# run pyflakes and pytest
pipenv run pyflakes run.py mediaproxy tests && pipenv run pytest tests "$@"
