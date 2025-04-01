# Link Shortener API

A high-performance URL shortening service built with FastAPI, Async SQLAlchemy, and Redis caching. Supports link shortening, click tracking, bulk operations, and analytics.

## Features

- Create short aliases for long URLs
- Track link clicks
- Bulk link creation
- Get original URL from short code
- View link statistics
- Search for existing short links
- Redis caching for improved performance
- JWT authentication for protected endpoints

## API Endpoints

### Link Management

| Method | Endpoint                | Description                          | Auth Required |
|--------|-------------------------|--------------------------------------|---------------|
| POST   | `/links/shorten`        | Create a new short link              | No            |
| POST   | `/links/bulk-shorten`   | Create multiple short links at once  | Yes           |
| GET    | `/links/{short_code}`   | Get original URL from short code     | No            |
| PUT    | `/links/{short_code}`   | Update a short link's destination    | Yes           |
| DELETE | `/links/{short_code}`   | Delete a short link                  | Yes           |

### Analytics

| Method | Endpoint                    | Description                          |
|--------|-----------------------------|--------------------------------------|
| GET    | `/links/{short_code}/stats` | Get click statistics for a link      |
| POST   | `/links/{short_code}/click` | Track a click and get redirect URL   |

### Search

| Method | Endpoint      | Description                          |
|--------|---------------|--------------------------------------|
| GET    | `/links/search?full_link={url}` | Find existing short links for a URL |

## Background Tasks

The system includes automated background processing via Celery:

### Expired Link Cleanup
- **Task**: `check_expired_links`
- **Schedule**: Runs every minute
- **Functionality**:
  - Scans the database for links where `expires_at` ≤ current time
  - Automatically deletes expired links
  - Returns count of deleted links
- **Error Handling**: Logs errors and continues operation

## Monitoring Background Tasks

When running in production, you can monitor background tasks using:

1. **Flower** - Celery monitoring tool (included in Docker setup)
   ```bash
   docker-compose up flower

## Request Examples

### Create Short Link
```bash
POST /links/shorten
Content-Type: application/json

{
  "full_link": "https://example.com/very/long/url",
  "short_link": "example"
}

Response:
{
  "status": "success"
}