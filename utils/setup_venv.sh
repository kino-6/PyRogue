#!/bin/bash

# Specify the Python version
PYTHON_VERSION="3.10.11"
venv="venv"

# Create a directory for the virtual environment
mkdir ${venv}

# Create a virtual environment with the specified Python version
python -m venv venv --prompt=${venv}

# Activate the virtual environment
source ${venv}/Scripts/activate

# Upgrade pip to the latest version
python -m pip install -U pip

# Deactivate the virtual environment
# deactivate

# Note: To reactivate the virtual environment in the future, use:
# source venv/bin/activate
