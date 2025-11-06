#!/usr/bin/env bash
set -euo pipefail

# Packages the example FastAPI app into a zip suitable for AWS Lambda (zip with requirements installed).
# This script creates a temporary folder, installs dependencies, copies source, and zips.

OUT=build/lambda_package.zip
rm -rf build
mkdir -p build

python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt -t build/python

cp lambda_handler.py build/

pushd build
zip -r ../lambda_package.zip .
popd

echo "Packaged $OUT"
