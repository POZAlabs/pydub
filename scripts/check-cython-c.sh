#!/usr/bin/env bash
for pyx in "$@"; do
  c="${pyx%.pyx}.c"
  if ! git diff --cached --name-only -- "$c" | grep -q .; then
    echo "ERROR: $pyx is staged but $c is not. Run 'uv build --sdist' first."
    exit 1
  fi
done
