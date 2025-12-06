# Backend API Tests

This directory contains test suites for the backend API.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest configuration and fixtures
├── test_auth.py         # Authentication tests
├── test_notifications.py # Notification API tests
├── test_privacy.py      # Privacy controls tests
├── test_wellbeing.py    # Wellbeing API tests
└── test_devices.py      # Device management tests
```

## Running Tests

### Run all tests
```bash
cd backend-api
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_auth.py -v
```

### Run with coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run in CI mode (fail fast)
```bash
pytest tests/ -x --tb=short
```

## Test Coverage Goals

- Unit tests: 80%+ coverage
- Integration tests: Key API endpoints
- Error handling: Edge cases and failures
- Security: Authentication and authorization

## Writing Tests

Use pytest fixtures from `conftest.py`:

```python
def test_example(client, auth_headers):
    response = client.get("/api/endpoint", headers=auth_headers)
    assert response.status_code == 200
```
