#!/bin/bash

# ------------------------------------------------------------------------------
#
# BOOTER: ATLASPH
#
# USAGE:
#     Force dependencies install: sh boot.sh -i true
#     Skip dependencies install:  sh boot.sh -i false
#
# ------------------------------------------------------------------------------


PATH_BIN_PYTHON="/usr/bin/python"
PATH_BIN_PIP="$(which pip)"

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PATH_APP="$CURRENT_DIR/app"

param_install=""
install_requirements=false

# If the install command-line param is null, go ahead with install of all
# requirements.txt dependencies

echo "[ATLASPH] Booting."
cd "$PATH_APP"

# Use getopts to pull the -i param from the commandline, to determine whether
# requirements install is being requested or explicityly denied

while getopts i: opts; do
  case ${opts} in
    i) param_install="${OPTARG}";;

  esac
done

if [ -n "$param_install" ]; then
  if [ "$param_install" = "false" ]; then
    install_requirements=false

  fi
fi

# If requirements should be installed (yes by default) go forward with the
# install procedure before running.

if $install_requirements; then
  echo "[ATLASPH] Installing system requirements."
  sudo $PATH_BIN_PIP install -r requirements.txt > logs/runtime_output.txt 2> logs/runtime_errors.txt

else
  echo "[ATLASPH] Skipping system requirements install."

fi

# Run the service

echo "[ATLASPH] Starting service."

$PATH_BIN_PYTHON boot.py
