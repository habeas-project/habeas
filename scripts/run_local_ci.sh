#!/bin/bash

# Script to run the local GitHub Actions CI workflow using act via yarn,
# capturing output to a timestamped log file.

# Requires act to be installed: https://github.com/nektos/act

# Ensure the script is run from the project root
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( dirname "$SCRIPT_DIR" )

cd "$PROJECT_ROOT" || exit 1

# Define log directory and ensure it exists
LOG_DIR="temp/logs"
mkdir -p "$LOG_DIR"

# Generate timestamped log file name
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/local_ci_run_$TIMESTAMP.log"

# Inform the user where the log is being saved
echo "Running local CI workflow via 'yarn test:ci:local'..."
echo "Output will be logged to: $LOG_FILE"

# Execute the yarn script and redirect all output (stdout & stderr) to the log file
yarn test:ci:local &> "$LOG_FILE"

EXIT_CODE=$?

# Check the exit code and report status
if [ $EXIT_CODE -eq 0 ]; then
  echo "Local CI run completed successfully. See log for details: $LOG_FILE"
else
  echo "Local CI run failed with exit code $EXIT_CODE. Check log for details: $LOG_FILE"
fi

exit $EXIT_CODE
