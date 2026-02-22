# API Status Checker

A FastAPI-based service that monitors API status pages using conditional HTTP polling. Automatically detects and logs incidents, outages, and degradations from status feeds.

Deployed on - [apistatuschecker-production.up.railway.app](https://apistatuschecker-production.up.railway.app/)


## Features

- **Conditional HTTP Polling**: Efficient event-driven polling using ETag headers
- **Async Background Processing**: Non-blocking background task that polls status feeds
- **Automatic Incident Detection**: Parses RSS/Atom feeds and logs new incidents
- **REST API Endpoints**: Health check and incidents viewing via HTTP
- **In-Memory Incident Storage**: Keeps track of recent incidents (last 20) for easy access
- **Configurable**: Environment-based configuration for feed URL and poll interval

## How It Works

The application uses **conditional HTTP polling** with async scheduling:

1. **Polling**: The service polls the status page feed at configured intervals (default: 60 seconds)
2. **Conditional Requests**: Uses `If-None-Match` (ETag) headers for efficient polling
3. **Efficient Updates**:
   - Server returns `304 Not Modified` when nothing changed → no data transfer
   - Server returns `200 OK` with new data when incidents are updated
4. **Event Processing**: New incidents are automatically parsed and logged
5. **Async**: All polling happens in background without blocking API requests

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## Installation

### Local Setup

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd APIStatusChecker
   ```

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:

   **Windows (PowerShell):**

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

   **Windows (Command Prompt):**

   ```cmd
   venv\Scripts\activate.bat
   ```

   **Linux/Mac:**

   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables** (optional):

   ```bash
   # Copy example env file
   cp .env.example .env

   # Edit .env with your settings
   ```

## Configuration

The service can be configured via environment variables:

- **STATUS_FEED_URL**: Status page feed URL (Atom or RSS format)
  - Default: `https://status.openai.com/feed.atom`
- **POLL_INTERVAL**: Polling interval in seconds
  - Default: `60`

Example `.env` file:

```env
STATUS_FEED_URL=https://status.openai.com/feed.atom
POLL_INTERVAL=60
```

## Running the Application

### Option 1: Run Locally (Development)

**From the `src` directory:**

```bash
cd src
uvicorn app:app --reload
```

**From the project root:**

```bash
# Windows (PowerShell)
$env:PYTHONPATH="src"
uvicorn src.app:app --reload

# Windows (Command Prompt)
set PYTHONPATH=src
uvicorn src.app:app --reload

# Linux/Mac
PYTHONPATH=src uvicorn src.app:app --reload
```

### Option 2: Run with Docker

1. **Build the Docker image**:

   ```bash
   docker build -t api-status-checker .
   ```

2. **Run the container**:

   ```bash
   docker run -p 8000:8000 api-status-checker
   ```

3. **Run with environment variables**:

   ```bash
   docker run -p 8000:8000 \
     -e STATUS_FEED_URL=https://status.openai.com/feed.atom \
     -e POLL_INTERVAL=30 \
     api-status-checker
   ```

4. **Run in detached mode** (background):

   ```bash
   docker run -d -p 8000:8000 --name api-status-checker api-status-checker
   ```

5. **View logs**:

   ```bash
   docker logs -f api-status-checker
   ```

6. **Stop the container**:
   ```bash
   docker stop api-status-checker
   docker rm api-status-checker
   ```

## API Endpoints

Once the application is running, it will be available at `http://localhost:8000`.

### Health Check

- **Endpoint:** `GET /api/health`
- **Description:** Returns the health status of the service
- **Response:**
  ```json
  {
    "status": "health ok",
    "timestamp": "2026-02-22T12:00:00+00:00"
  }
  ```

### Recent Incidents

- **Endpoint:** `GET /api/incidents`
- **Description:** Returns recent incidents detected from the status feed
- **Response:**
  ```json
  {
    "feed_url": "https://status.openai.com/feed.atom",
    "poll_interval": 60,
    "count": 2,
    "incidents": [
      {
        "id": "incident-123",
        "title": "API Performance Degradation",
        "summary": "We are currently investigating increased latency...",
        "updated": "2026-02-22T12:00:00+00:00"
      },
      {
        "id": "incident-122",
        "title": "Service Resolved",
        "summary": "All systems are now operational.",
        "updated": "2026-02-22T11:30:00+00:00"
      }
    ]
  }
  ```
## Monitoring Incidents

When the application is running, it automatically polls the configured status page feed in the background. New incidents are:

1. **Logged to console** with the following format:
   ```
   [2026-02-22 12:00:00] Product: API Performance Degradation
   Status: We are currently investigating increased latency...
   ```

2. **Stored in memory** and accessible via the `/api/incidents` endpoint

3. **Automatically tracked** - The service keeps the last 20 incidents for easy viewing

You can view incidents by:
- **API Endpoint**: `GET /api/incidents` - Returns JSON with all recent incidents
- **Application Logs**: Check console output or Docker logs for real-time updates

**Note**: Incidents will appear after the service has polled the feed and detected updates. If no incidents have been detected yet, the `incidents` array will be empty.

## Project Structure

```
APIStatusChecker/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── health.py         # Health check endpoint
│   │   ├── status.py         # Incidents endpoint
│   │   └── monitor.py        # Background polling service
│   ├── services/
│   │   ├── __init__.py
│   │   └── status_monitor.py # Status feed monitoring service
│   └── app.py                 # FastAPI application entry point
├── .env.example               # Environment variables example
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
└── README.md                  # This file
```
