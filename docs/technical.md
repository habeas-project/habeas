# Habeas - Technical Documentation

## Development Requirements

### System Dependencies

The following system-level dependencies are required for development:

#### PostgreSQL and Development Package

The PostgreSQL development package is required for building the `psycopg2-binary` Python package during dependency installation.

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install libpq-dev postgresql
```

**macOS (with Homebrew):**
```bash
brew install postgresql
```

#### Yarn Package Manager

Yarn is required for JavaScript dependency management and running project scripts.

**Ubuntu/Debian:**
```bash
# Option 1: Add the official Yarn repository
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
sudo apt update
sudo apt install yarn

# Option 2: Install via npm 
sudo npm install -g yarn
```

**macOS (with Homebrew):**
```bash
brew install yarn
```

### Python Environment Setup

1. Make sure you have Python 3.12+ installed
2. Install uv for Python package management:
   ```bash
   pip install uv
   ```
3. Install system dependencies (including PostgreSQL development files)
4. Run the setup commands from the README.md

#### Python Command

On many systems, `python` refers to Python 2.x, while `python3` refers to Python 3.x. The scripts in package.json should use the appropriate command for your system. If you encounter a "python: not found" error, update the scripts to use `python3` instead.

#### Virtual Environment Activation

The Python dependencies are installed in a virtual environment located in the `apps/backend/.venv` directory. If you encounter module import errors, you may need to activate the virtual environment before running Python commands:

```bash
# From the apps/backend directory
source .venv/bin/activate
```

Alternatively, update the package.json scripts to activate the virtual environment before running Python commands:

```json
"dev:backend": "cd apps/backend && source .venv/bin/activate && python3 -m uvicorn app.main:app --reload"
```

### Python Dependencies

The following Python packages are installed via `uv sync`:

- alembic==1.10.4
- anyio==4.9.0
- click==8.1.8
- fastapi==0.95.1
- greenlet==3.1.1
- h11==0.14.0
- idna==3.10
- mako==1.3.9
- markupsafe==3.0.2
- psycopg2-binary==2.9.6
- pydantic==1.10.7
- python-dotenv==1.0.0
- sniffio==1.3.1
- sqlalchemy==2.0.12
- starlette==0.26.1
- typing-extensions==4.13.1
- uvicorn==0.22.0

## Common Issues

### pg_config executable not found

**Error:**
```
error: pg_config executable not found
```

**Solution:**
This error occurs when trying to build psycopg2 without the PostgreSQL development files installed. Install the appropriate package for your system as described in the "PostgreSQL Development Package" section above.

### Python module not found

**Error:**
```
No module named 'uvicorn' (or any other module)
```

**Solution:**
This usually means you're not running Python from the virtual environment where the packages were installed. Activate the virtual environment before running Python commands or update your scripts to do so automatically (see "Virtual Environment Activation" section). 