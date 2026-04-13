#! /bin/bash

# Set any pipeline to return the last non-zero status
# so that we can capture an error in uv run pytest
# even after piping its stdout into tee
set -uo pipefail

# Run in repo's python/ directory
cd "${GITHUB_WORKSPACE}/python/"

# --cov-report=markdown-append is not supported
# for pytest versions compatible with Python 3.8,
# so we manually append the terminal output
# to $GITHUB_STEP_SUMMARY

echo '```' >> "${GITHUB_STEP_SUMMARY}"

uv run pytest \
  --cov=parsled \
  --cov-report=term-missing \
  "${GITHUB_WORKSPACE}/python/tests/" \
  | tee --append "${GITHUB_STEP_SUMMARY}"

TEST_EXIT_CODE="${?}"

echo '```' >> "${GITHUB_STEP_SUMMARY}"

exit "${TEST_EXIT_CODE}"
