#!/bin/bash

pushd $(dirname ${BASH_SOURCE[0]}) > /dev/null

CMD="flake8 --exit-zero ceryle/ tests/; pytest $*"

chokidar \
  ceryle/*.py \
  ceryle/**/*.py \
  tests/*.py \
  tests/**/*.py \
  -c "$CMD" \
  --initial
