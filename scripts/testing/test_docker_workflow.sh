#!/usr/bin/env bash

# Test the Docker Compose workflow including migrations and data population
# This script follows the Habeas Core Principles and best practices

set -e  # Exit immediately if a command exits with non-zero status

# Record script start time for timing information (moved earlier for total duration)
START_TIME=$(date +%s)
SCRIPT_DIR="$(dirname "$0")"

# Navigate to project root first
# echo "Navigating to project root..." # Logged later by log function
cd "$(dirname "$0")/../.."
ROOT_DIR="$(pwd)"

# --- Log file setup ---
# Placed early so log function can be defined and used ASAP
LOG_FILE="$ROOT_DIR/temp/logs/docker_workflow_test_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# --- Log function ---
# Defines how messages are logged and saved.
log() {
    local message="$1"
    local level="${2:-INFO}" # Default to INFO level
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log "Initializing Docker workflow test script..."
log "Project root: $ROOT_DIR"
log "Logs will be saved to $LOG_FILE"

# --- Load timing helper functions ---
# Must be sourced after 'log' is defined if its functions call 'log' directly,
# or if 'log' is passed as an argument and called within.
source "${SCRIPT_DIR}/time_steps.sh"

# --- Environment file setup ---
ENV_FILE="$ROOT_DIR/.env"
ENV_EXAMPLE_FILE="$ROOT_DIR/.env.example"

if [ ! -f "$ENV_FILE" ]; then
    if [ -f "$ENV_EXAMPLE_FILE" ]; then
        log "Creating .env file from $ENV_EXAMPLE_FILE..."
        cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
        log ".env file created. Please review and update $ENV_FILE with your local settings if necessary."
    else
        log ".env file not found and $ENV_EXAMPLE_FILE does not exist. This may cause issues." "ERROR"
        # exit 1 # Decide if this is critical enough to exit
    fi
fi

if [ -f "$ENV_FILE" ]; then
    log "Loading environment variables from $ENV_FILE"
    set -a # Automatically export all variables defined in the .env file
    source "$ENV_FILE"
    set +a # Stop automatically exporting
else
    log ".env file not found at $ENV_FILE. Relying on existing environment variables." "WARN"
fi

# --- Argument parsing ---
VERBOSE=false
SKIP_CLEANUP=false
HELP=false

show_help() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Test the Docker Compose workflow including migrations and data population."
  echo ""
  echo "Options:"
  echo "  -v, --verbose       Enable verbose output (sets VERBOSE=true)."
  echo "  --skip-cleanup    Skip cleanup of Docker containers and volumes on exit."
  echo "  -h, --help          Show this help message and exit."
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -v|--verbose)
      VERBOSE=true
      log "Verbose mode enabled." "DEBUG"
      shift # past argument
      ;;
    --skip-cleanup)
      SKIP_CLEANUP=true
      log "Cleanup on exit will be skipped." "INFO"
      shift # past argument
      ;;
    -h|--help)
      HELP=true
      shift # past argument
      ;;
    *)    # unknown option
      log "Unknown option: $1" "WARN"
      shift # past argument
      ;;
  esac
done

# Show help text if requested
if [ "$HELP" = true ]; then
  show_help
  exit 0
fi

# --- Docker Compose command helper ---
# Function to run docker compose commands with appropriate flags and logging
run_docker_compose() {
    local cmd_args=("$@")
    # Determine Docker Compose files to use
    local compose_files=("-f" "apps/docker-compose.yml") # Base compose file

    # Check for environment-specific override file at root
    if [ -f "docker-compose.dev.yml" ]; then
        compose_files+=("-f" "docker-compose.dev.yml")
    # Or check in apps/ directory
    elif [ -f "apps/docker-compose.dev.yml" ]; then
        compose_files+=("-f" "apps/docker-compose.dev.yml")
    fi

    # Check for E2E override file if applicable (example, adjust as needed)
    # if [ -f "docker-compose.e2e.yml" ]; then
    #     compose_files+=("-f" "docker-compose.e2e.yml")
    # fi

    log "Executing Docker Compose: docker compose ${compose_files[*]} ${cmd_args[*]}" "DEBUG"

    if [ "$VERBOSE" = true ]; then
        docker compose "${compose_files[@]}" "${cmd_args[@]}" | tee -a "$LOG_FILE"
    else
        docker compose "${compose_files[@]}" "${cmd_args[@]}" >> "$LOG_FILE" 2>&1
    fi
    local status=$?
    if [ $status -ne 0 ]; then
        log "Docker compose command failed with exit code $status: docker compose ${compose_files[*]} ${cmd_args[*]}" "ERROR"
    fi
    return $status
}

# --- Cleanup function ---
# Registered with trap to run on script exit
cleanup() {
    log "Script finishing. Performing cleanup..."
    if [ "$SKIP_CLEANUP" = true ]; then
        log "Skipping cleanup as per --skip-cleanup flag."
    else
        log "Stopping containers and removing volumes..."
        run_docker_compose down -v --remove-orphans # Added --remove-orphans
        log "Cleanup complete."
    fi

    local end_script_time=$(date +%s)
    local total_duration=$((end_script_time - START_TIME))
    log "Total script execution time: ${total_duration}s"

    # Print step summary if timing functions were used
    if type get_step_summary &>/dev/null; then
        log "$(get_step_summary)"
    fi
    log "Script finished. Logs are available at $LOG_FILE"
}

# Register the cleanup function to execute on script exit (EXIT, INT, TERM)
trap cleanup EXIT SIGINT SIGTERM

# --- Main test workflow ---
log "Starting Docker workflow test."

# Clean start
log "Performing initial cleanup: stopping any existing containers and removing volumes..."
run_docker_compose down -v --remove-orphans

# Pull latest images (optional, can be time-consuming)
# log "Pulling latest images..."
# run_docker_compose pull

# Build services
log "Building services..."
run_docker_compose build

# Start the database
start_timing "database_startup"
log "Starting the database service (db)..."
run_docker_compose up -d db
log "Waiting for database to be ready..."

# Check database connection with retries
# Variables like POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB should be from .env
# For pg_isready, POSTGRES_HOST should be where the port is exposed (localhost for host script)
DB_HOST_CHECK="${POSTGRES_HOST_FOR_CHECK:-127.0.0.1}"
DB_PORT_CHECK="${POSTGRES_PORT_FOR_CHECK:-5432}"

MAX_DB_RETRIES=12  # Approx 60 seconds (12 * 5s)
DB_RETRY_INTERVAL=5
DB_RETRY_COUNT=0
DB_READY=false

log "Attempting to connect to database at $DB_HOST_CHECK:$DB_PORT_CHECK as user $POSTGRES_USER for database $POSTGRES_DB..."
while [ $DB_RETRY_COUNT -lt $MAX_DB_RETRIES ] && [ "$DB_READY" = false ]; do
    if PGPASSWORD=$POSTGRES_PASSWORD pg_isready -h "$DB_HOST_CHECK" -p "$DB_PORT_CHECK" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -q; then
        log "Database is ready."
        DB_READY=true
        end_timing "database_startup" log
    else
        log "Database not ready yet. Retrying in $DB_RETRY_INTERVAL seconds... (Attempt $((DB_RETRY_COUNT + 1))/$MAX_DB_RETRIES)"
        sleep $DB_RETRY_INTERVAL
        DB_RETRY_COUNT=$((DB_RETRY_COUNT + 1))
    fi
done

if [ "$DB_READY" = false ]; then
    log "Database did not become ready after $MAX_DB_RETRIES attempts." "ERROR"
    log "Attempting to get logs from db container..."
    run_docker_compose logs db
    exit 1
fi

# Run migrations
start_timing "database_migrations"
log "Running database migrations using 'migration' service..."
run_docker_compose run --rm --service-ports migration # Use run --rm for one-off tasks
# Alternative: run_docker_compose up --exit-code-from migration migration (if 'migration' is defined to exit)
# The current docker-compose.yml uses `command: python /app/run_migrations.py` which implies it's a one-off task.
# `up --exit-code-from` is good for this.
run_docker_compose up --exit-code-from migration migration
MIGRATION_STATUS=$?

if [ $MIGRATION_STATUS -eq 0 ]; then
    log "Database migrations completed successfully."
    end_timing "database_migrations" log
else
    log "Database migrations failed. Exit code: $MIGRATION_STATUS" "ERROR"
    log "Attempting to get logs from migration task..."
    # 'up --exit-code-from' might not leave logs easily accessible if container is removed.
    # If using 'run --rm', logs are on stdout/stderr.
    # For 'up', use 'logs' command:
    run_docker_compose logs migration
    exit 1
fi

# Run data ingestion
start_timing "data_ingestion"
log "Running data ingestion using 'data-ingestion' service..."
run_docker_compose up --exit-code-from data-ingestion data-ingestion
INGESTION_STATUS=$?

if [ $INGESTION_STATUS -eq 0 ]; then
    log "Data ingestion completed successfully."
    end_timing "data_ingestion" log
else
    log "Data ingestion failed. Exit code: $INGESTION_STATUS" "ERROR"
    log "Attempting to get logs from data-ingestion task..."
    run_docker_compose logs data-ingestion
    exit 1
fi

# Run backend with full database
start_timing "backend_startup"
log "Starting backend service for testing..."
run_docker_compose up -d backend # Start backend in detached mode
log "Waiting for backend to start and become healthy..."
# Initial sleep can be helpful but the loop is the main check
sleep 5

# Test backend API health endpoint
HEALTH_ENDPOINT="http://localhost:8000/health" # Assuming backend runs on port 8000
MAX_API_RETRIES=12 # Approx 60 seconds
API_RETRY_INTERVAL=5
API_RETRY_COUNT=0
API_READY=false

log "Checking backend API health at $HEALTH_ENDPOINT..."
while [ $API_RETRY_COUNT -lt $MAX_API_RETRIES ] && [ "$API_READY" = false ]; do
    # Use curl: -f to fail on HTTP errors, -s for silent, -L to follow redirects
    if curl -fsL "$HEALTH_ENDPOINT" > /dev/null; then
        log "Backend API is healthy."
        API_READY=true
        end_timing "backend_startup" log
    else
        log "Backend API not healthy yet. Retrying in $API_RETRY_INTERVAL seconds... (Attempt $((API_RETRY_COUNT + 1))/$MAX_API_RETRIES)"
        sleep $API_RETRY_INTERVAL
        API_RETRY_COUNT=$((API_RETRY_COUNT + 1))
    fi
done

if [ "$API_READY" = false ]; then
    log "Backend API did not become healthy after $MAX_API_RETRIES attempts." "ERROR"
    log "Attempting to get logs from backend container..."
    run_docker_compose logs backend
    exit 1
fi

# Verify database content
start_timing "database_verification"
log "Verifying database content using verify_migration.py..."
# This script is expected to be at /app/data/pipeline/4_verification/verify_migration.py inside the container
# We can run it using the 'backend' service context as it has the necessary mounts and Python env.
run_docker_compose run --rm backend python /app/data/pipeline/4_verification/verify_migration.py
VERIFICATION_STATUS=$?

if [ $VERIFICATION_STATUS -eq 0 ]; then
    log "Database verification successful."
    end_timing "database_verification" log
else
    log "Database verification failed. Exit code: $VERIFICATION_STATUS" "ERROR"
    # Output from the script should have been logged by run_docker_compose
    exit 1
fi

log "Docker workflow test completed successfully!"
# Cleanup will run automatically via trap
exit 0
