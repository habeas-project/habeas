# Docker Workflow Testing

This directory contains scripts for testing and validating the Docker Compose workflow for the Habeas project.

## Scripts

### `test_docker_workflow.sh`

Tests the complete Docker Compose workflow including database setup, migrations, data ingestion, and backend API verification.

#### Usage

```bash
# Run from project root
./scripts/testing/test_docker_workflow.sh [options]

# Available options:
#  --verbose, -v       Enable verbose output
#  --skip-cleanup      Don't remove containers after testing
#  --help, -h          Show help message
```

#### What it tests

1. **Environment Setup**: Verifies .env file exists or creates it from .env.example
2. **Database Startup**: Tests PostgreSQL container startup
3. **Migrations**: Runs and verifies Alembic database migrations
4. **Data Ingestion**: Executes the data ingestion pipeline
5. **Backend Service**: Starts the backend service and tests the health endpoint
6. **Data Verification**: Verifies that required tables exist with expected data

#### Logs

Logs are saved to `temp/logs/docker_workflow_test_YYYYMMDD_HHMMSS.log` for each test run.

#### Timing and Performance Analysis

The test script includes detailed timing information for each step of the workflow:
- Database startup
- Database migrations
- Data ingestion
- Backend service startup
- Database verification

This timing information helps identify bottlenecks in the workflow and track performance improvements over time.

## Requirements

- Docker and Docker Compose installed on your system
- Valid `.env` file in project root or `.env.example` to create one from
- Network access to pull Docker images if not already available locally

## Integration with Other Testing

This workflow script is complementary to the unit and integration tests run with `run_tests.sh`.
While those tests focus on code correctness, this script validates the operational workflow
of services working together in Docker containers.
