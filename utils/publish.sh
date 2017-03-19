#!/usr/bin/env bash
#####################################################################
# publish.sh
# Author: Tim Legrand - 2015
#####################################################################
# Description of the script goes here...
# to here.
#####################################################################


### If running interactively
if [ "$PS1" ]; then echo -e "This script cannot be sourced. Use \"./${0}\" instead." ; return ; fi


### Usage
usage() {
  echo "Usage: publish.sh ACTION [--remote <alias>]"
  echo ""
  echo "Options:"
  echo ""
  echo "  ACTION must be one of the following:"
  echo ""
  echo "    register: Registers package with the remote."
  echo "    build:    Build distributions."
  echo "    upload:   Upload package to the remote."
  echo ""
  echo "  --remote:   The remote to which the action will apply."
  echo "              The remote must have been previously configured in your '~/.pypirc' file."
  echo "              Default is 'test'."
  echo ""
}


register() {
  python setup.py register -r $remote
}


build() {
  python setup.py sdist bdist_wheel --universal
}


upload() {
  twine upload -r $remote dist/* --sign
}


clean() {
  echo -n "Cleaning... "
  rm -rf build/
  rm -rf dist/
  rm -rf *.egg-info/
  rm -rf .tox/
  pyclean .
  echo "OK."
}


### Initialize default values
remote="test"


### Check if args are correctly given
while [ $# -gt 0 ] ; do
  case ${1} in
    --remote)
      shift
      if [ $# -gt 0 ] ; then
        remote="${1}"
        shift
      else
        usage
        exit 1
      fi
      ;;
    register)
      action="register"
      shift
      ;;
    build)
      action="build"
      shift
      ;;
    upload)
      action="upload"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

if [ -z ${action} ] ; then usage ; exit 1 ; fi  # An action is mandatory


### Main goes here...
case ${action} in
  register)
    register
    ;;
  build)
    clean
    build
    ;;
  upload)
    clean
    build
    upload
    ;;
  *)
    usage
    exit 1
    ;;
esac
