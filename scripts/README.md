# Habeas Scripts Directory

This directory contains all automation scripts for the Habeas project, organized by category for easy discovery and maintenance.

## 📁 Directory Structure

```
scripts/
├── README.md                    # This file - overview of all scripts
├── development/                 # Development environment scripts
│   ├── start_manual_testing.sh  # Start backend for manual testing
│   └── update_wsl_ip.sh         # Update WSL IP configuration
├── mobile/                      # Mobile app development scripts
│   ├── start_mobile_app.sh      # Start mobile app with cache clearing
│   └── clear_mobile_cache.sh    # Clear all mobile app caches
├── testing/                     # Testing automation scripts
│   ├── README.md               # Testing scripts documentation
│   ├── run_tests.py            # Python test runner
│   ├── run_tests.sh            # Shell test runner
│   ├── test_docker_workflow.sh # Docker workflow testing
│   └── time_steps.sh           # Performance timing utilities
├── run_local_ci.sh             # Run complete local CI pipeline
└── setup_android_studio.sh     # Android Studio setup automation
```

## 🚀 Quick Start Scripts

### **Mobile Development**
```bash
# Start complete mobile development environment
~/habeas/scripts/mobile/start_mobile_app.sh

# Clear mobile app caches when encountering issues
~/habeas/scripts/mobile/clear_mobile_cache.sh
```

### **Backend Development**
```bash
# Start backend for manual testing
~/habeas/scripts/development/start_manual_testing.sh

# Update WSL IP configuration (WSL environments only)
~/habeas/scripts/development/update_wsl_ip.sh
```

### **Testing**
```bash
# Run complete local CI pipeline
~/habeas/scripts/run_local_ci.sh

# Run specific test suites
~/habeas/scripts/testing/run_tests.sh
```

## 📱 Mobile Development Scripts

### `mobile/start_mobile_app.sh`
**Purpose**: Complete mobile app startup with automatic cache clearing and tunnel mode

**Features**:
- Clears Expo and Metro caches automatically
- Updates WSL IP configuration
- Validates backend connectivity
- Starts Expo with tunnel mode for reliable connections
- Provides comprehensive startup instructions

**Usage**:
```bash
~/habeas/scripts/mobile/start_mobile_app.sh
```

**Requirements**:
- Backend must be running (use `start_manual_testing.sh` first)
- Android emulator should be running in Windows (for WSL users)

### `mobile/clear_mobile_cache.sh`
**Purpose**: Standalone cache clearing for troubleshooting mobile app issues

**Use Cases**:
- App showing old screens after code changes
- "No apps connected" errors when reloading
- Stale JavaScript bundles
- Connection issues with development server

**Usage**:
```bash
~/habeas/scripts/mobile/clear_mobile_cache.sh
```

**What it clears**:
- `.expo` directory
- `node_modules/.cache`
- Metro bundler caches
- npm cache
- Watchman cache (if available)

## 🔧 Development Environment Scripts

### `development/start_manual_testing.sh`
**Purpose**: Start backend services for manual testing and development

**Features**:
- Starts PostgreSQL database via Docker Compose
- Runs database migrations
- Starts FastAPI backend server
- Validates all services are running correctly

**Usage**:
```bash
~/habeas/scripts/development/start_manual_testing.sh
```

**Services Started**:
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- API documentation (http://localhost:8000/docs)

### `development/update_wsl_ip.sh`
**Purpose**: Update IP configuration for WSL environments

**Features**:
- Automatically detects current WSL IP address
- Updates `.env` files with correct IP
- Updates mobile app configuration
- Provides restart instructions

**Usage**:
```bash
~/habeas/scripts/development/update_wsl_ip.sh
```

**When to use**:
- WSL IP address has changed
- Mobile app can't connect to backend
- After WSL restart

## 🧪 Testing Scripts

### `testing/run_tests.py` & `testing/run_tests.sh`
**Purpose**: Comprehensive test execution with multiple options

**Features**:
- Unit tests, integration tests, and end-to-end tests
- Coverage reporting
- Parallel test execution
- Test result aggregation

**Usage**:
```bash
# Python version (recommended)
~/habeas/scripts/testing/run_tests.py --coverage

# Shell version
~/habeas/scripts/testing/run_tests.sh
```

### `testing/test_docker_workflow.sh`
**Purpose**: Test Docker-based workflows and container interactions

**Usage**:
```bash
~/habeas/scripts/testing/test_docker_workflow.sh
```

## 🏗️ Setup & CI Scripts

### `run_local_ci.sh`
**Purpose**: Run complete local continuous integration pipeline

**Features**:
- Linting and code formatting
- Type checking
- Full test suite execution
- Build validation
- Performance benchmarks

**Usage**:
```bash
~/habeus/scripts/run_local_ci.sh
```

### `setup_android_studio.sh`
**Purpose**: Automated Android Studio and emulator setup

**Features**:
- Android SDK installation
- Emulator configuration
- Environment variable setup
- Development tools installation

**Usage**:
```bash
~/habeas/scripts/setup_android_studio.sh
```

## 🔍 Troubleshooting

### Common Issues

**Mobile app showing old screens**:
```bash
~/habeas/scripts/mobile/clear_mobile_cache.sh
~/habeas/scripts/mobile/start_mobile_app.sh
```

**Backend connection issues**:
```bash
~/habeas/scripts/development/update_wsl_ip.sh
~/habeas/scripts/development/start_manual_testing.sh
```

**Test failures**:
```bash
~/habeas/scripts/testing/run_tests.sh --verbose
```

### Script Dependencies

**Mobile Development Flow**:
1. `development/start_manual_testing.sh` (start backend)
2. `mobile/start_mobile_app.sh` (start mobile app)

**Full Development Setup**:
1. `setup_android_studio.sh` (one-time setup)
2. `development/update_wsl_ip.sh` (as needed)
3. `development/start_manual_testing.sh` (backend)
4. `mobile/start_mobile_app.sh` (mobile app)

## 📝 Script Maintenance

### Adding New Scripts
1. Place in appropriate subdirectory (`development/`, `mobile/`, `testing/`)
2. Make executable: `chmod +x script_name.sh`
3. Update this README with documentation
4. Add to relevant workflow documentation

### Script Standards
- Use `#!/bin/bash` shebang
- Include comprehensive error handling
- Provide clear status messages
- Include usage instructions in comments
- Follow existing naming conventions

### Path References
- Use absolute paths: `~/habeas/scripts/...`
- Update cross-references when moving scripts
- Test script paths after reorganization

---

*For questions or issues with scripts, see project documentation or create an issue.*
