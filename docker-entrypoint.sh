#!/usr/bin/env bash

set -o errexit

# Remove any .pyc, .pyo or __pycache__ files because they will probably be from
# the local machine and thus a different platform. That would confuse tox.
echo "Removing any .pyc, .pyo or __pycache__ files"
find /app | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

# Run the command
exec "$@"
