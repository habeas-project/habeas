#!/usr/bin/env python3
"""
Habeas Test Runner

A utility script for running tests in the Habeas project with flexible options.
Allows running all tests or specific types (unit, integration, etc.) with custom parameters.
"""

import argparse
import os
import subprocess
import sys
from typing import List

# Project paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "apps", "backend")
BACKEND_TESTS_DIR = os.path.join(BACKEND_DIR, "tests")
# Add mobile paths
MOBILE_DIR = os.path.join(PROJECT_ROOT, "apps", "mobile")
MOBILE_E2E_DIR = os.path.join(MOBILE_DIR, "tests", "e2e")


class TestRunner:
    """Runs Habeas tests with configurable options"""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.docker = args.docker
        self.verbose = args.verbose

    def run(self) -> int:
        """Execute tests based on provided arguments"""
        test_type = self.args.test_type

        if test_type == "backend":
            if self.args.list_markers:
                return self._list_backend_markers()
            print("--- Running Backend Tests (pytest) ---")
            return self._run_backend_tests()
        elif test_type == "mobile":
            if self.args.e2e:
                print("--- Running Mobile E2E Tests (Maestro) ---")
                return self._run_mobile_e2e_tests()
            else:
                print("--- Running Mobile Unit/Integration Tests (Jest) ---")
                return self._run_mobile_unit_tests()
        else:
            # Default or 'all' case (currently runs backend + mobile unit)
            # TODO: Consider how 'all' should behave (include E2E?)
            print("--- Running Backend Tests (pytest) ---")
            backend_result = self._run_backend_tests()
            print("\n--- Running Mobile Unit/Integration Tests (Jest) ---")
            mobile_unit_result = self._run_mobile_unit_tests()
            print(
                "\nNote: Mobile E2E tests (Maestro) must be run explicitly with --type mobile --e2e."
            )
            return backend_result or mobile_unit_result

    # --- Backend Test Execution ---

    def _run_backend_tests(self) -> int:
        """Runs backend tests using pytest."""
        pytest_args = self._build_pytest_args()
        if self.verbose:
            print(f"Running pytest command: {' '.join(pytest_args)}")

        if self.docker:
            return self._run_backend_in_docker(pytest_args)
        else:
            return self._run_backend_locally(pytest_args)

    def _build_pytest_args(self) -> List[str]:
        """Build the pytest command arguments for backend tests"""
        cmd = ["pytest"]

        # Add verbosity if requested
        if self.args.verbose:
            cmd.append("-v")

        # Add coverage if requested
        if self.args.coverage:
            cmd.extend(["--cov=app", "--cov-report=term"])
            if self.args.coverage_html:
                cmd.append("--cov-report=html")

        # Add JUnit XML report if requested
        if self.args.junit_xml:
            cmd.extend(["--junitxml", self.args.junit_xml])

        # Add markers based on test type (relevant for backend tests)
        # These flags might be less relevant now with --type but kept for filtering
        markers = []
        if self.args.unit:
            markers.append("unit")
        if self.args.integration:
            markers.append("integration")
        if self.args.slow:
            markers.append("slow")

        if markers and not self.args.run_all_backend:  # Use new flag
            marker_expr = " or ".join(markers)
            cmd.extend(["-m", marker_expr])

        # Add failing first if requested
        if self.args.failing_first:
            cmd.append("--failed-first")

        # Add specific test paths if provided
        if self.args.paths:
            cmd.extend(self.args.paths)
        else:
            cmd.append(BACKEND_TESTS_DIR)  # Default to backend tests dir

        # Add any additional pytest arguments
        if self.args.pytest_args:
            cmd.extend(self.args.pytest_args)

        return cmd

    def _run_backend_locally(self, pytest_args: List[str]) -> int:
        """Run backend tests locally"""
        os.chdir(BACKEND_DIR)
        # Prefix command with uv run if using uv
        if self.args.use_uv:
            pytest_args = ["uv", "run"] + pytest_args
        try:
            print(f"Executing locally: {' '.join(pytest_args)}")
            return subprocess.call(pytest_args)
        except Exception as e:
            print(f"Error running backend tests locally: {e}")
            return 1

    def _run_backend_in_docker(self, pytest_args: List[str]) -> int:
        """Run backend tests in Docker container"""
        # Change to project root for docker compose
        os.chdir(PROJECT_ROOT)

        # Create docker compose command to run pytest in the backend container
        # Assumes docker-compose.test.yml or similar defines the service
        docker_cmd = [
            "docker",
            "compose",
            "-f",
            "docker-compose.yml",
            "-f",
            "docker-compose.test.yml",  # Assuming test overrides
            "run",
            "--rm",
        ]

        # Add build arg if we need to ensure dev dependencies
        if self.args.build:
            docker_cmd.extend(["--build", "--build-arg", "INSTALL_DEV=true"])

        docker_cmd.append("backend")  # Service name

        # For docker, always use uv to run pytest
        final_cmd = docker_cmd + ["uv", "run"] + pytest_args

        if self.verbose:
            print(f"Executing Docker command: {' '.join(final_cmd)}")

        try:
            return subprocess.call(final_cmd)
        except Exception as e:
            print(f"Error running backend tests in Docker: {e}")
            return 1

    def _list_backend_markers(self) -> int:
        """List available pytest markers for backend tests"""
        os.chdir(BACKEND_DIR)
        try:
            cmd = (
                ["uv", "run", "pytest", "--markers"]
                if self.args.use_uv
                else ["pytest", "--markers"]
            )
            return subprocess.call(cmd)
        except Exception as e:
            print(f"Error listing backend markers: {e}")
            return 1

    # --- Mobile Test Execution ---

    def _run_mobile_unit_tests(self) -> int:
        """Run mobile unit/integration tests using Jest."""
        os.chdir(MOBILE_DIR)
        cmd = ["yarn", "test"]  # Assumes 'test' script in mobile package.json runs Jest

        # Pass through coverage flag if provided (and supported by jest script)
        if self.args.coverage:
            cmd.append("--coverage")

        # Pass through any extra path arguments to Jest
        if self.args.paths:
            cmd.extend(self.args.paths)

        # Note: Running Jest tests in Docker is complex due to native dependencies.
        if self.docker:
            print(
                "Warning: Running mobile Jest tests via Docker is not supported by this script. Running locally."
            )

        try:
            print(f"Executing Jest command: {' '.join(cmd)}")
            return subprocess.call(cmd)
        except Exception as e:
            print(f"Error running mobile unit tests: {e}")
            return 1

    def _run_mobile_e2e_tests(self) -> int:
        """Run mobile end-to-end tests using Maestro."""
        # Requires Maestro CLI to be installed separately
        os.chdir(MOBILE_E2E_DIR)  # Navigate to E2E directory

        cmd = ["maestro", "test"]

        flow_path = "flows"  # Default directory for flows
        if self.args.paths:
            # Allow specifying a specific flow file or directory relative to e2e dir
            flow_path = self.args.paths[0]

        cmd.append(flow_path)

        # E2E tests often require manual setup (simulators, backend running)
        # Consider adding checks or setup steps here if automating further
        print(f"Executing Maestro command: {' '.join(cmd)} in {MOBILE_E2E_DIR}")
        print(
            "Ensure backend services are running (docker-compose up ...), a simulator/device is available, and the mobile app is built/running."
        )

        try:
            return subprocess.call(cmd)
        except FileNotFoundError:
            print(
                "Error: 'maestro' command not found. Is Maestro CLI installed and in your PATH?"
            )
            return 1
        except Exception as e:
            print(f"Error running mobile E2E tests: {e}")
            return 1


def parse_args() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run Habeas tests for different suites (backend, mobile)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backend tests locally using uv
  python scripts/testing/run_tests.py --type backend --use-uv

  # Run backend unit tests in Docker
  python scripts/testing/run_tests.py --type backend --docker --unit

  # Run backend tests with coverage report
  python scripts/testing/run_tests.py --type backend --use-uv --coverage

  # Run mobile unit tests (Jest)
  python scripts/testing/run_tests.py --type mobile

  # Run mobile unit tests with coverage
  python scripts/testing/run_tests.py --type mobile --coverage

  # Run mobile E2E tests (Maestro) for all flows
  python scripts/testing/run_tests.py --type mobile --e2e

  # Run a specific mobile E2E test flow
  python scripts/testing/run_tests.py --type mobile --e2e flows/specific_flow.yml

  # Run all backend tests and mobile unit tests
  python scripts/testing/run_tests.py --type all --use-uv
""",
    )

    # Test Suite Selection
    parser.add_argument(
        "--type",
        dest="test_type",
        choices=["backend", "mobile", "all"],
        default="all",  # Default to running backend + mobile unit
        help="Type of tests to run (default: all = backend pytest + mobile jest)",
    )

    # --- Backend Specific Options ---
    backend_group = parser.add_argument_group(
        "Backend Options (when --type is backend or all)"
    )
    backend_group.add_argument(
        "--docker", action="store_true", help="Run backend tests in Docker container"
    )
    backend_group.add_argument(
        "--use-uv",
        action="store_true",
        help="Use uv to run backend pytest (for local runs)",
    )
    backend_group.add_argument(
        "--build",
        action="store_true",
        help="Build Docker container before running backend tests",
    )
    # Backend Test Filtering (Markers)
    backend_group.add_argument(
        "--unit", action="store_true", help="Run backend unit tests (pytest -m unit)"
    )
    backend_group.add_argument(
        "--integration",
        action="store_true",
        help="Run backend integration tests (pytest -m integration)",
    )
    backend_group.add_argument(
        "--slow",
        action="store_true",
        help="Run backend tests marked as slow (pytest -m slow)",
    )
    backend_group.add_argument(
        "--run-all-backend",
        action="store_true",
        help="Run all backend tests (ignoring markers like unit/integration/slow)",
    )
    backend_group.add_argument(
        "--list-markers",
        action="store_true",
        help="List available pytest markers for backend tests and exit",
    )
    backend_group.add_argument(
        "--failing-first",
        action="store_true",
        help="Run previously failing backend tests first (pytest --failed-first)",
    )
    backend_group.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass directly to pytest",
    )

    # --- Mobile Specific Options ---
    mobile_group = parser.add_argument_group("Mobile Options (when --type is mobile)")
    mobile_group.add_argument(
        "--e2e",
        action="store_true",
        help="Run Mobile E2E tests (Maestro) instead of unit tests (Jest)",
    )

    # --- General Options (Applicable to multiple types) ---
    general_group = parser.add_argument_group("General & Report Options")
    general_group.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report (pytest --cov / jest --coverage)",
    )
    general_group.add_argument(
        "--coverage-html",
        action="store_true",
        help="Generate HTML coverage report (pytest only)",
    )
    general_group.add_argument(
        "--junit-xml",
        metavar="FILE",
        help="Generate JUnit XML report (pytest only)",
    )
    general_group.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    general_group.add_argument(
        "paths",
        nargs="*",
        help="Specific test paths/files to run (relative to test suite root, e.g., tests/unit/some_test.py or flows/my_flow.yml)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point"""
    args = parse_args()
    runner = TestRunner(args)
    return runner.run()


if __name__ == "__main__":
    sys.exit(main())
