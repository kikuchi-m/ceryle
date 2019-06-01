#!/bin/bash

pushd $(dirname ${BASH_SOURCE[0]}) > /dev/null

chokidar \
  ceryle/*.py \
  ceryle/**/*.py \
  tests/*.py \
  tests/**/*.py \
  -c "pytest $*" \
  --initial
