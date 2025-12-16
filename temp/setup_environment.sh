#!/bin/bash

echo "Starting Environment Setup..."

# 1. Install Intel Fortran Runtime (Fix for libifport.so.5 error)
# Only runs if the library is missing (checks for setvars.sh)
if [ ! -f "/opt/intel/oneapi/setvars.sh" ] && [ ! -f "/opt/intel/oneapi/compiler/latest/env/vars.sh" ]; then
    echo "Intel Fortran Runtime not found. Installing..."
    # Add Intel repository
    wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | gpg --dearmor | sudo tee /usr/share/keyrings/oneapi-archive-keyring.gpg > /dev/null
    echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | sudo tee /etc/apt/sources.list.d/oneAPI.list
    
    sudo apt-get update
    sudo apt-get install -y intel-oneapi-compiler-fortran-runtime
else
    echo "Intel Fortran Runtime appears to be installed."
fi

# 2. Setup Python 3.12 Environment
# This checks for Python 3.12 and creates a venv
if [ ! -d ".venv" ]; then
    echo "Setting up Python 3.12..."
    # Install Python 3.12 if missing
    if ! command -v python3.12 &> /dev/null; then
        echo "Python 3.12 not found. Installing..."
        sudo apt-get update
        sudo apt-get install -y python3.12 python3.12-venv
    fi
    
    # Create venv in the current directory (project root)
    python3.12 -m venv .venv
    echo "Created .venv in project root"
else
    echo "Virtual environment .venv already exists."
fi

echo "Environment setup complete."
