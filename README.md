# robo-advisor

A Python FastAPI application with TortoiseORM backend that stores data in a SQLite database.

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **TortoiseORM** - Async ORM for Python with SQLite support
- **SQLite** - Lightweight, file-based database
- **Pydantic** - Data validation using Python type annotations
- **Async/Await** - Full async support for high performance

## API Endpoints

### Portfolios
- `POST /api/v1/portfolios` - Create a new portfolio
- `GET /api/v1/portfolios` - List all portfolios
- `GET /api/v1/portfolios/{id}` - Get a specific portfolio
- `PUT /api/v1/portfolios/{id}` - Update a portfolio
- `DELETE /api/v1/portfolios/{id}` - Delete a portfolio

### Assets
- `POST /api/v1/assets` - Create a new asset
- `GET /api/v1/assets` - List all assets (optional ?portfolio_id filter)
- `GET /api/v1/assets/{id}` - Get a specific asset
- `PUT /api/v1/assets/{id}` - Update an asset
- `DELETE /api/v1/assets/{id}` - Delete an asset

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Running the Application

```bash
# Start the server
uvicorn app.main:app --reload

# The API will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
# Alternative docs at http://localhost:8000/redoc
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py -v
```

## Example Usage

```bash
# Create a portfolio
curl -X POST http://localhost:8000/api/v1/portfolios \
  -H "Content-Type: application/json" \
  -d '{"name": "My Portfolio", "description": "Tech stocks"}'

# Create an asset
curl -X POST http://localhost:8000/api/v1/assets \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "quantity": "10.5",
    "purchase_price": "150.25"
  }'

# List all portfolios
curl http://localhost:8000/api/v1/portfolios

# List assets for a specific portfolio
curl http://localhost:8000/api/v1/assets?portfolio_id=1
```

## Database

The application uses SQLite as the database backend. The database file `db.sqlite3` is created automatically on first run in the project root directory.

### Models

- **Portfolio**: Represents an investment portfolio with name and description
- **Asset**: Represents a financial asset with symbol, name, quantity, and purchase price

## Development

The project uses:
- **Ruff** for linting and formatting
- **Pytest** for testing with async support
- **pytest-asyncio** for async test fixtures

## Project Structure

```
robo-advisor/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application
│   ├── models.py        # TortoiseORM models
│   ├── schemas.py       # Pydantic schemas
│   ├── routes.py        # API routes
│   └── database.py      # Database configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py      # Test configuration
│   ├── test_api.py      # API endpoint tests
│   └── test_models.py   # Model tests
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
└── README.md
```

## License

See LICENSE file for details.