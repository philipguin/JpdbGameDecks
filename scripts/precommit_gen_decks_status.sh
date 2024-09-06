#!/bin/bash

python scripts/gen_decks_status.py
status=$?
if [ $status -ne 0 ]; then
  echo "'python scripts/gen_decks_status.py' failed ($status)"
  exit $status
fi

git add docs/_includes/deck-metrics.html docs/_includes/decks-body.html
