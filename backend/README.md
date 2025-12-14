# HealthGuard Backend API

FastAPI-based backend service providing REST APIs for the HealthGuard AI platform.

## Features

- **RESTful API**: Versioned API endpoints
- **WebSocket Support**: Real-time updates
- **Event Streaming**: Kafka integration
- **Database**: PostgreSQL with async support
- **Caching**: Redis integration
- **Authentication**: JWT-based auth
- **Documentation**: Auto-generated OpenAPI/Swagger docs

## Structure

```
backend/
├── api/              # API routes and endpoints
├── services/         # Business logic
├── db/               # Database models and migrations
├── events/           # Event producers/consumers
├── integrations/     # External service integrations
└── workers/          # Background tasks
```

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
