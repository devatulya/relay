#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers and its system dependencies
# In Render, we might need to use playwright install --with-deps chromium
playwright install --with-deps chromium
