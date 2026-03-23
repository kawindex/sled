#! /bin/bash

# Run in repo's python/ directory
cd "${GITHUB_WORKSPACE}/python/"

if [ ${UV_PYTHON} = "3.8" ]; then
  # pytest --cov-report=markdown-append not supported for Python 3.8
  echo '```' >> "${GITHUB_STEP_SUMMARY}"
  uv run pytest \
    --cov=pysled \
    --cov-report=term-missing \
    "${GITHUB_WORKSPACE}/python/tests/" \
    | tee --append "${GITHUB_STEP_SUMMARY}"
  echo '```' >> "${GITHUB_STEP_SUMMARY}"
else
  uv run pytest \
    --cov=pysled \
    --cov-report=term-missing \
    --cov-report="markdown-append:${GITHUB_STEP_SUMMARY}" \
    "${GITHUB_WORKSPACE}/python/tests/"
fi
