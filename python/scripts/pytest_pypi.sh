#! /bin/bash

# Set any pipeline to return the last non-zero status
# so that we can capture an error in uv run pytest
# even after piping its stdout into tee
set -uo pipefail

# Run in repo's python/ directory
cd "${GITHUB_WORKSPACE}/python/"

# --cov-report=markdown-append only appends the coverage report.
# When testing the distribution, we are more concerned with
# test results than coverage, so across all Python versions,
# we take the terminal output and manually append it
# to $GITHUB_STEP_SUMMARY

echo '```' >> "${GITHUB_STEP_SUMMARY}"

uv run \
  --isolated \
  --no-project \
  --no-cache \
  --index "https://pypi.org/simple/" \
  --index "https://test.pypi.org/simple/" \
  --with parsled \
  --with pytest \
  --with pytest-cov \
  pytest \
    --cov=parsled \
    --cov-report=term-missing \
    "${GITHUB_WORKSPACE}/python/tests/" \
| tee --append "${GITHUB_STEP_SUMMARY}"

TEST_EXIT_CODE="${?}"

echo '```' >> "${GITHUB_STEP_SUMMARY}"

exit "${TEST_EXIT_CODE}"
