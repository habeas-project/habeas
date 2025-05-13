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

# Back up existing .env file if it exists
if [ -f ".env" ]; then
  echo "Backing up existing .env file to .env.bak"
  cp .env .env.bak
fi

# Create a fresh .env file for CI testing
echo "Creating CI .env file for testing..."
cat > .env << EOL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=testpassword
POSTGRES_DB=habeas
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql://postgres:testpassword@db:5432/habeas
SECRET_KEY=ci_temp_secret_key_123456789_abcdefghi #gitleaks:allow
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:19006
EOL
echo "CI .env file created"

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible. Please start Docker and try again."
  exit 1
fi

# Inform the user where the log is being saved
echo "Running local CI workflow via 'yarn test:ci:local'..."
echo "Output will be logged to: $LOG_FILE"

# Execute the yarn script and redirect all output (stdout & stderr) to the log file
yarn test:ci:local &> "$LOG_FILE"

EXIT_CODE=$?

# Indicate that the main command has finished running
echo "Script finished. Checking results..."

# Restore the original .env file if it existed
if [ -f ".env.bak" ]; then
  echo "Restoring original .env file from .env.bak"
  mv .env.bak .env
fi

# Check the exit code and report status
if [ $EXIT_CODE -eq 0 ]; then
  echo "Local CI run completed successfully. See log for details: $LOG_FILE"
else
  echo "Local CI run failed with exit code $EXIT_CODE. Check log for details: $LOG_FILE"
  # Show the last few lines of the log to help debug issues
  echo "Last few error lines:"
  grep -A 20 "❌  Failure" "$LOG_FILE" | head -n 10
fi

exit $EXIT_CODE
