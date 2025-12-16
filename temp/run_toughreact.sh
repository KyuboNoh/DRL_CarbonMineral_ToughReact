#!/bin/bash

export OMP_NUM_THREADS=$(nproc)

PWD=$(pwd)
TOUGHREACT_MAIN_PATH="$PWD/.TOUGHREACT"
TOUGHREACT_EXEC_NAME="treactv413omp_eco2n_linux"
TOUGHREACT_EXEC_PATH="$TOUGHREACT_MAIN_PATH/TEMP_EXEC/"
# TOUGHREACT_INPUT_FILES_PATH="$TOUGHREACT_MAIN_PATH/P6_eco2n/P6_eco2n_2D-radial"
TOUGHREACT_INPUT_FILES_PATH="$TOUGHREACT_MAIN_PATH/Deepsky_1_example"


# 1. Create the TOUGHREACT directory if it doesn't exist
mkdir -p "$TOUGHREACT_EXEC_PATH"

# 2. Copy and RENAME your specific input files to the FIXED names required by TOUGHREACT
cp "$TOUGHREACT_INPUT_FILES_PATH"/* "$TOUGHREACT_EXEC_PATH/"

# 2b. Copy the executable to the execution directory
cp "$TOUGHREACT_MAIN_PATH/$TOUGHREACT_EXEC_NAME" "$TOUGHREACT_EXEC_PATH/"
chmod +x "$TOUGHREACT_EXEC_PATH/$TOUGHREACT_EXEC_NAME"

# TEMPORARY: Copy generated "INCON" file to the execution directory for automatic debugging
cp ./INCON "$TOUGHREACT_EXEC_PATH/" 2>/dev/null || :

# 3. Change directory to the TOUGHREACT execution directory
cd "$TOUGHREACT_EXEC_PATH"

# 4. Run TOUGHREACT
# Source Intel oneAPI environment variables to find libifport.so.5
if [ -f "/opt/intel/oneapi/setvars.sh" ]; then
    source /opt/intel/oneapi/setvars.sh > /dev/null
elif [ -f "/opt/intel/oneapi/compiler/latest/env/vars.sh" ]; then
    source /opt/intel/oneapi/compiler/latest/env/vars.sh > /dev/null
fi

# Increase stack size to prevent SIGSEGV (Segmentation Fault)
ulimit -s unlimited

./$TOUGHREACT_EXEC_NAME
