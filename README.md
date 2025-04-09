# Habeas

Habeas is an open-source project designed to help detained individuals connect with legal representatives who can file habeas corpus petitions on their behalf.

The goal of this project is to make it easier for people to meet that burden by rapidly pairing detained individuals with legal representatives who are able to file those petitions on their behalf and in the appropriate jurisdictions.

## Repository Structure

This is a monorepo containing:

- A React Native mobile application (apps/mobile)
- A FastAPI backend service (apps/backend)

For detailed architecture information, see [docs/architecture.md](docs/architecture.md).
For technical requirements and troubleshooting, see [docs/technical.md](docs/technical.md).

## Getting Started

### Prerequisites

- Node.js 16+
- Yarn Classic (v1)
- Python 3.12+
- uv (Python package manager)
- PostgreSQL
- PostgreSQL development package (libpq-dev on Ubuntu/Debian)

### Setup

1. Clone this repository
```
git clone https://github.com/yourusername/habeas.git
cd habeas
```

2. Install JavaScript dependencies
```
yarn install
```

3. Set up the Python environment
```
# From the root directory
yarn backend:install-dev
```

4. Copy the environment file and configure it
```
cd apps/backend
cp .env.example .env
# Edit .env with your database credentials and settings
```

5. Start the development servers

Backend:
```
# In the root directory
yarn dev:backend
```

Mobile app:
```
# In the root directory
yarn dev:mobile
```

For iOS:
```
yarn ios
```

For Android:
```
yarn android
```

## Contributing

Contributions are welcome! Please see our [contributing guidelines](CONTRIBUTING.md) for more information.

## License

[Your License Here]
