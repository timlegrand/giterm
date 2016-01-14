#!/usr/bin/env sh

rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf .tox/
rm -rf .cache
rm -rf cover/
rm -rf .coverage

pyclean .
