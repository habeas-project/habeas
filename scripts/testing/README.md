# Habeas Test Runner

A flexible utility for running the Habeas test suite with various options and configurations.

## Overview

The test runner provides a unified way to run tests across different environments (local or Docker) with customizable options for test selection, reporting, and more.

## Usage

```bash
# Basic usage
./scripts/testing/run_tests.sh [options]

# View help information
./scripts/testing/run_tests.sh --help
```

## Common Use Cases

### Running Specific Test Types

```bash
# Run only unit tests
./scripts/testing/run_tests.sh --unit

# Run only integration tests
./scripts/testing/run_tests.sh --integration

# Run only slow tests
./scripts/testing/run_tests.sh --slow

# Run both unit and integration tests
./scripts/testing/run_tests.sh --unit --integration
```

### Running Tests in Different Environments

```bash
# Run tests locally using uv (recommended for local development)
./scripts/testing/run_tests.sh --use-uv

# Run tests in Docker (similar to CI environment)
./scripts/testing/run_tests.sh --docker

# Run tests in Docker with fresh build
./scripts/testing/run_tests.sh --docker --build
```

### Generating Reports

```bash
# Generate test coverage report
./scripts/testing/run_tests.sh --coverage

# Generate HTML coverage report
./scripts/testing/run_tests.sh --coverage --coverage-html

# Generate JUnit XML report for CI integration
./scripts/testing/run_tests.sh --junit-xml=test-results.xml
```

### Running Specific Tests

```bash
# Run a specific test file
./scripts/testing/run_tests.sh tests/unit/test_specific.py

# Run tests in a specific directory
./scripts/testing/run_tests.sh tests/integration/

# Run specific test with additional pytest arguments
./scripts/testing/run_tests.sh tests/unit/test_auth.py --pytest-args -k "test_login_success"
```

## Options Reference

### Environment Options
- `--docker`: Run tests in Docker container
- `--use-uv`: Use uv to run pytest (for local runs)
- `--build`: Build Docker container before running tests

### Test Type Options
- `--unit`: Run unit tests
- `--integration`: Run integration tests
- `--slow`: Run tests marked as slow
- `--all`: Run all tests (regardless of markers)

### Report Options
- `--coverage`: Generate coverage report
- `--coverage-html`: Generate HTML coverage report
- `--junit-xml FILE`: Generate JUnit XML report at specified path

### General Options
- `--verbose, -v`: Enable verbose output
- `--list-markers`: List available pytest markers and exit
- `--failing-first`: Run previously failing tests first

## CI Integration

The test runner is configured to work seamlessly with our CI pipeline. The CI configuration in `.github/workflows/test.yml` runs tests similar to:

```bash
./scripts/testing/run_tests.sh --docker --build --coverage --junit-xml=test-results.xml
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Make sure scripts are executable:
   ```bash
   chmod +x scripts/testing/run_tests.py scripts/testing/run_tests.sh
   ```

2. **Docker not running**: Ensure Docker daemon is running before using the `--docker` flag.

3. **Missing dependencies**: When running locally, ensure all test dependencies are installed:
   ```bash
   cd apps/backend && uv pip install -e ".[dev]"
   ```
