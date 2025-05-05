#!/bin/bash

# Habeas Test Runner Shell Wrapper
# This script provides a simple shell wrapper around the Python test runner

# --- Configuration ---
# Find the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/run_tests.py"
# Updated compose file reference (though might not need specific E2E one if simple)
# Using a generic name for clarity, assuming standard docker-compose.yml might be used
# or a specific one just for backend/db if needed.
# Let's keep E2E_COMPOSE_FILE for now, assuming it defines db_e2e and backend_e2e
E2E_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.e2e.yml"
LOG_DIR="$PROJECT_ROOT/temp/logs"

# --- Helper Functions ---
log() {
  if ! $NO_LOG; then
    echo "$@" | tee -a "$LOG_FILE"
  else
    echo "$@"
  fi
}

# Cleanup function for E2E Docker backend/db environment
e2e_cleanup() {
  if [[ -n "$E2E_ENV_STARTED" ]]; then
    log "--- Stopping E2E Docker Backend/DB Environment ---"
    # Stop only the backend and db services
    docker-compose -f "$E2E_COMPOSE_FILE" stop db_e2e backend_e2e
    # Optional: Bring down if needed, but stop might be sufficient
    # docker-compose -f "$E2E_COMPOSE_FILE" down --remove-orphans
    log "E2E Docker Backend/DB Environment stopped."
  fi
}

# --- Initialization ---
# Ensure logs directory exists
mkdir -p "$LOG_DIR"

# Create a log file with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/test_run_$TIMESTAMP.log"

# Set trap for cleanup
trap e2e_cleanup EXIT INT TERM

# --- Parse Arguments --- #
TEST_TYPE="all" # Default to all (backend + mobile unit)
DOCKER_ARG=""
E2E_ARG=""
VERBOSE_ARG=""
COVERAGE_ARG=""
NO_LOG=false
PYTEST_ARGS=()
FORWARDED_ARGS=() # Args to pass directly to python script
E2E_ENV_STARTED="" # Flag to track if we started the E2E env

# Use associative array for easier flag management
declare -A PY_ARGS

while [[ $# -gt 0 ]]; do
  case $1 in
    --type)
      TEST_TYPE="$2"
      shift 2
      ;;
    --docker)
      PY_ARGS["--docker"]=1
      shift
      ;;
    --e2e)
      # This flag now primarily signifies needing the backend/db + host emulator
      E2E_ARG="--e2e" # Store separately for env check
      PY_ARGS["--e2e"]=1
      shift
      ;;
    --verbose|-v)
      PY_ARGS["--verbose"]=1
      shift
      ;;
    --coverage)
      PY_ARGS["--coverage"]=1
      shift
      ;;
    # --- Add other python script flags here as needed ---
    --use-uv)
      PY_ARGS["--use-uv"]=1
      shift
      ;;
    --build)
      PY_ARGS["--build"]=1
      shift
      ;;
    --unit)
      PY_ARGS["--unit"]=1
      shift
      ;;
    --integration)
      PY_ARGS["--integration"]=1
      shift
      ;;
    --slow)
      PY_ARGS["--slow"]=1
      shift
      ;;
    --run-all-backend)
      PY_ARGS["--run-all-backend"]=1
      shift
      ;;
    --list-markers)
      PY_ARGS["--list-markers"]=1
      shift
      ;;
     --failing-first)
      PY_ARGS["--failing-first"]=1
      shift
      ;;
     --coverage-html)
      PY_ARGS["--coverage-html"]=1
      shift
      ;;
     --junit-xml)
       PY_ARGS["--junit-xml"]="$2"
       shift 2
       ;;
    # --- Shell script specific flags ---
    --no-log)
      NO_LOG=true
      shift
      ;;
    --) # Stop parsing flags, treat remaining as paths/pytest args
      shift
      FORWARDED_ARGS+=("$@")
      break
      ;;
    *) # Assume it's a path or pytest arg
      FORWARDED_ARGS+=("$1")
      shift
      ;;
  esac
done

# --- Environment Setup / Checks --- #

# Function to check if docker is needed and running
check_docker() {
  # Docker check is implicitly handled by docker-compose if needed
  if ! command -v docker &> /dev/null; then
    log "Error: docker command not found. Please install Docker."
    exit 1
  fi
  if ! command -v docker-compose &> /dev/null; then
     # Try docker compose (v2)
     if ! docker compose version &> /dev/null; then
       log "Error: docker-compose / 'docker compose' command not found. Please install Docker Compose."
       exit 1
     fi
     # Use v2 syntax if v1 not found
     DOCKER_COMPOSE_CMD="docker compose"
  else
     DOCKER_COMPOSE_CMD="docker-compose"
  fi
  log "Docker command found."
}

# Function to check mobile prerequisites
check_mobile_reqs() {
  if [[ "$TEST_TYPE" == "mobile" || "$TEST_TYPE" == "all" ]]; then
    # Check for yarn
    if ! command -v yarn &> /dev/null; then
        log "Error: yarn is required for mobile tests but not found."
        exit 1
    fi
    # Check for E2E specific requirements
    if [[ -n "$E2E_ARG" ]]; then
        # Check for Maestro
        if ! command -v maestro &> /dev/null; then
          log "Error: Maestro is required for mobile E2E tests (--type mobile --e2e) but is not installed."
          log "Please install it via: curl -Ls https://get.maestro.mobile.dev | bash"
          exit 1
        fi
        log "Maestro CLI found."

        # Check for adb (Android Debug Bridge)
        if ! command -v adb &> /dev/null; then
            log "Error: adb (Android Debug Bridge) is required for mobile E2E tests but not found."
            log "Please install Android SDK Platform Tools and ensure adb is in your PATH."
            exit 1
        fi
        log "adb command found."
    fi
  fi
}

# Run checks
log "--- Running Pre-Checks --- "
check_docker
check_mobile_reqs
log "Pre-checks complete."


# --- Construct Python Command --- #
CMD_ARGS=("python3" "$PYTHON_SCRIPT" "--type" "$TEST_TYPE")

# Add parsed flags
for flag in "${!PY_ARGS[@]}"; do
  # Handle flags that take values vs boolean flags
  if [[ "$flag" == "--junit-xml" ]]; then
      CMD_ARGS+=("$flag" "${PY_ARGS[$flag]}")
  elif [[ "${PY_ARGS[$flag]}" -eq 1 ]]; then
      CMD_ARGS+=("$flag")
  fi
done

# Add remaining arguments (paths, pytest args)
CMD_ARGS+=("${FORWARDED_ARGS[@]}")

# Join command arguments for execution and logging
CMD="$(printf '%q ' "${CMD_ARGS[@]}")"

# --- Execute Tests --- #

# If running mobile E2E, check for host emulator and start backend/db
if [[ -n "$E2E_ARG" && "$TEST_TYPE" == "mobile" ]]; then
  log "--- Checking for Host Android Emulator/Device ---"
  # Get list of devices, skip header lines
  ADB_DEVICES_OUTPUT=$(adb devices | tail -n +2)
  # Filter out empty lines and count remaining lines
  NUM_DEVICES=$(echo "$ADB_DEVICES_OUTPUT" | sed '/^\s*$/d' | wc -l)

  if [[ $NUM_DEVICES -eq 0 ]]; then
    log "Error: No connected Android devices or emulators found."
    log "Please start an emulator (e.g., via Android Studio) or connect a physical device."
    log "Ensure the device is authorized and listed by 'adb devices' on your host machine."
    exit 1
  elif [[ $NUM_DEVICES -gt 1 ]]; then
      log "Warning: Multiple devices/emulators found. Maestro will target the first one listed by 'adb devices'."
      log "Connected devices:\n$ADB_DEVICES_OUTPUT"
  fi

  # Get the ID of the first device/emulator found
  TARGET_DEVICE_ID=$(echo "$ADB_DEVICES_OUTPUT" | sed '/^\s*$/d' | head -n 1 | awk '{print $1}')
  TARGET_DEVICE_STATUS=$(echo "$ADB_DEVICES_OUTPUT" | sed '/^\s*$/d' | head -n 1 | awk '{print $2}')

  log "Found device: $TARGET_DEVICE_ID (Status: $TARGET_DEVICE_STATUS)"

  if [[ "$TARGET_DEVICE_STATUS" != "device" ]]; then
      log "Error: Device $TARGET_DEVICE_ID is not ready (Status: $TARGET_DEVICE_STATUS)."
      log "Please ensure the device is fully booted, unlocked, and authorized for debugging."
      exit 1
  fi

  # Check if device has booted
  log "Waiting for device $TARGET_DEVICE_ID to fully boot..."
  MAX_WAIT_BOOT=120 # seconds
  WAIT_INTERVAL=5 # seconds
  ELAPSED_WAIT=0
  BOOT_READY=false
  while [ $ELAPSED_WAIT -lt $MAX_WAIT_BOOT ]; do
      BOOT_COMPLETED=$(adb -s "$TARGET_DEVICE_ID" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r\n')
      if [[ "$BOOT_COMPLETED" == "1" ]]; then
          log "Device $TARGET_DEVICE_ID has booted."
          BOOT_READY=true
          break
      else
          log "Device $TARGET_DEVICE_ID not fully booted yet (getprop: $BOOT_COMPLETED). Waiting $WAIT_INTERVAL seconds..."
      fi
      sleep $WAIT_INTERVAL
      ELAPSED_WAIT=$((ELAPSED_WAIT + WAIT_INTERVAL))
  done

  if ! $BOOT_READY; then
      log "Error: Device $TARGET_DEVICE_ID did not report boot completion within $MAX_WAIT_BOOT seconds."
      exit 1
  fi

  # Now start the backend/db services
  log "--- Starting E2E Docker Backend/DB Environment ---"
  log "Using compose file: $E2E_COMPOSE_FILE"

  if $DOCKER_COMPOSE_CMD -f "$E2E_COMPOSE_FILE" up --build -d db_e2e backend_e2e; then
    log "E2E backend/db starting..."
    E2E_ENV_STARTED="true" # Set flag for cleanup trap

    # --- Wait for Backend Service --- #
    log "Waiting for backend_e2e service to become healthy..."
    MAX_WAIT_BACKEND=60 # seconds
    WAIT_INTERVAL=5 # seconds
    ELAPSED_WAIT=0
    BACKEND_HEALTHY=false
    while [ $ELAPSED_WAIT -lt $MAX_WAIT_BACKEND ]; do
      # Try curling the health endpoint directly
      if curl --fail --silent --output /dev/null http://localhost:8000/health; then
        log "Backend service is healthy (responded to /health)."
        BACKEND_HEALTHY=true
        break
      fi

      # Log the current docker state for info
      CURRENT_STATUS=$($DOCKER_COMPOSE_CMD -f "$E2E_COMPOSE_FILE" ps --format "{{.State}}" backend_e2e 2>/dev/null || echo "unknown")
      log "Backend not healthy yet (Status: $CURRENT_STATUS, /health check failed). Waiting $WAIT_INTERVAL seconds..."
      sleep $WAIT_INTERVAL
      ELAPSED_WAIT=$((ELAPSED_WAIT + WAIT_INTERVAL))
    done

    if ! $BACKEND_HEALTHY; then
      log "Error: Backend service did not become healthy within $MAX_WAIT_BACKEND seconds."
      # Attempt to capture backend logs before exiting
      log "Attempting to capture backend logs..."
      $DOCKER_COMPOSE_CMD -f "$E2E_COMPOSE_FILE" logs backend_e2e || echo "Failed to get backend logs."
      exit 1
    fi
  else
    log "Error: Failed to start E2E Docker backend/db environment."
    exit 1
  fi
fi

# Inform user that tests are running
log "Running command: $CMD"
if ! $NO_LOG; then
  log "Test type: $TEST_TYPE. Log will be saved to: $LOG_FILE"
  # Run the Python test runner script and redirect output to log and stdout/stderr
  eval $CMD 2>&1 | tee -a "$LOG_FILE"
else
  log "Test type: $TEST_TYPE."
  # Run without logging to file
  eval $CMD
fi

# Store the exit code from the eval command
EXIT_CODE=${PIPESTATUS[0]}

# Extract and display a summary of the test results from the log file
if ! $NO_LOG && [ -f "$LOG_FILE" ]; then
  log "------------------------------------------------------------------------------"
  log "Test Summary (from $LOG_FILE):"
  log "------------------------------------------------------------------------------"

  # Pytest summary
  if grep -q -E '(===[=]+ .* seconds ====[=]+|PASSED|FAILED)' "$LOG_FILE"; then
      grep -E '(===[=]+ .* seconds ====[=]+|PASSED|FAILED)' "$LOG_FILE" | tail -n 1
  fi

  # Jest summary
  if grep -q -E '(Test Suites:|Tests:|Snapshots:|Time:)' "$LOG_FILE"; then
      grep -E '(Test Suites:|Tests:|Snapshots:|Time:)' "$LOG_FILE"
  fi

  # Maestro summary (less structured, look for Pass/Fail)
  if grep -q -E '(PASS|FAIL)' "$LOG_FILE"; then
      log "Maestro Results:"
      grep -E '(PASS|FAIL)' "$LOG_FILE"
  fi

  log "------------------------------------------------------------------------------"
  log "Tests finished with exit code: $EXIT_CODE. Full results available in: $LOG_FILE"
else
    echo "Tests finished with exit code: $EXIT_CODE."
fi

# Exit with the same code as the Python script
# Cleanup is handled by the trap
exit $EXIT_CODE
