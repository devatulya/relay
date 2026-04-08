#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers to a specific location that persists
export PLAYWRIGHT_BROWSERS_PATH=/opt/render/project/src/.cache/ms-playwright
playwright install chromium
