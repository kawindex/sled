#! /bin/bash

set -eu

export HTML_OUTPUT_DIR="${READTHEDOCS_OUTPUT}html"

echo "HTML output dir: ${HTML_OUTPUT_DIR}"

if [ -e "${HTML_OUTPUT_DIR}" ]; then
  rm --recursive "${HTML_OUTPUT_DIR}"
  echo "Deleted ${HTML_OUTPUT_DIR}"
fi

mkdir -p "${READTHEDOCS_OUTPUT}"
cp --recursive "python/docs/html" "${READTHEDOCS_OUTPUT}"

ls "${HTML_OUTPUT_DIR}"
