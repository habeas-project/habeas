#!/bin/bash

# Script to run the local GitHub Actions CI workflow using act via yarn,
# capturing output to a timestamped log file.
# This script does NOT modify your existing .env file.

# Requires act to be installed: https://github.com/nektos/act

set -euo pipefail  # Exit on error, undefined vars, pipe failures

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

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running or not accessible. Please start Docker and try again."
    exit 1
fi

# Create a temporary .env.ci file for the CI run (this won't affect your .env)
ENV_CI_FILE=".env.ci.tmp.$TIMESTAMP"

echo "Creating temporary CI environment file: $ENV_CI_FILE"
cat > "$ENV_CI_FILE" << EOL
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
ENABLE_MOCK_AUTH=true
EOL

# Function for cleanup
cleanup() {
    local exit_code=$?
    echo ""
    echo "=== Cleanup Phase ==="

    # Remove temporary CI env file
    if [ -f "$ENV_CI_FILE" ]; then
        rm -f "$ENV_CI_FILE"
        echo "Cleaned up temporary CI environment file"
    fi

    echo "Your original .env file was never modified."

    # Report final status
    if [ $exit_code -eq 0 ]; then
        echo "Local CI run completed successfully. See log for details: $LOG_FILE"
    else
        echo "Local CI run failed with exit code $exit_code. Check log for details: $LOG_FILE"
        # Show the last few lines of the log to help debug issues
        if [ -f "$LOG_FILE" ]; then
            echo "Last few error lines:"
            tail -n 20 "$LOG_FILE" | grep -E "(Error|Failed|❌)" | head -n 10 || true
        fi
    fi

    exit $exit_code
}

# Set up trap to ensure cleanup runs on any exit
trap cleanup EXIT

# Inform the user about the approach
echo "Running local CI workflow without modifying your .env file..."
echo "Using temporary CI environment: $ENV_CI_FILE"
echo "Output will be logged to: $LOG_FILE"

# Create the act command with environment file override
echo "=== Starting CI Run ===" | tee -a "$LOG_FILE"
echo "Timestamp: $(date)" | tee -a "$LOG_FILE"
echo "CI Environment file: $ENV_CI_FILE" | tee -a "$LOG_FILE"
echo "Original .env file: UNTOUCHED" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run act with environment variable file override
# We use --env-file to pass our CI environment to the GitHub Actions runner
act -W .github/workflows/test.yml --env-file "$ENV_CI_FILE" &>> "$LOG_FILE"

# Note: cleanup() will be called automatically via trap on script exit
