#!/bin/bash
set -ex

virtualenv -p python3 venv || true

source venv/bin/activate

pip install -r src/requirements.txt

export FLASK_APP="src/app.py"

python3 -m flask run
