#!/usr/bin/env bash

# Helper script for timing steps in our testing workflow
# Adds more sophisticated timing functionality to test_docker_workflow.sh

# Dictionary to store timings
declare -A STEP_TIMES
CURRENT_STEP=""

# Start timing a step
# Usage: start_timing "step_name"
start_timing() {
    CURRENT_STEP="$1"
    STEP_TIMES["${CURRENT_STEP}_start"]=$(date +%s)
}

# End timing a step and log the duration
# Usage: end_timing "step_name" "log_function"
end_timing() {
    local step="$1"
    local log_func="$2"

    if [[ -n "${STEP_TIMES["${step}_start"]}" ]]; then
        local end_time=$(date +%s)
        local start_time=${STEP_TIMES["${step}_start"]}
        local duration=$((end_time - start_time))

        STEP_TIMES["${step}_duration"]=$duration

        # Format duration nicely
        if [ $duration -lt 60 ]; then
            $log_func "Step '$step' completed in ${duration}s"
        else
            local minutes=$((duration / 60))
            local seconds=$((duration % 60))
            $log_func "Step '$step' completed in ${minutes}m ${seconds}s"
        fi
    else
        $log_func "Warning: No start time recorded for step '$step'"
    fi
}

# Get all step durations in a formatted table
# Usage: get_step_summary
get_step_summary() {
    local result="Step Timing Summary:\n"
    result+="-------------------\n"

    # Find all steps that have duration recorded
    for key in "${!STEP_TIMES[@]}"; do
        if [[ $key == *"_duration" ]]; then
            local step=${key%_duration}
            local duration=${STEP_TIMES[$key]}

            # Format duration nicely
            if [ $duration -lt 60 ]; then
                result+="${step}: ${duration}s\n"
            else
                local minutes=$((duration / 60))
                local seconds=$((duration % 60))
                result+="${step}: ${minutes}m ${seconds}s\n"
            fi
        fi
    done

    echo -e "$result"
}
