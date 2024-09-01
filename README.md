# Health Check Service

This Python service performs periodic health checks of `go-zenon` by sending requests to an endpoint and provides a health status via an HTTP API.

## Features

- Periodic health checks (default every 60 seconds)
- Returns HTTP 200 if the service is healthy, 500 if it is not
- Logs results and errors to syslog for centralized logging
- Configurable URL and check interval
- Rate limiting to prevent abuse (1 request per 15 seconds per IP)

## Prerequisites

- Python 3.6+
- Virtual environment (recommended)
- Systemd (for running as a service)

## Setup Instructions

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/0x3639/health-check-service.git
cd health-check-service
```

### 2. Create a Virtual Environment

Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configure the Service

You can configure the health check interval, the URL to be checked, and rate limiting by editing the following variables at the top of `health_check.py`:

```python
CHECK_INTERVAL = 60  # Health check interval in seconds
HEALTH_CHECK_URL = "http://127.0.0.1:35997"  # URL for the health check
```

- **`CHECK_INTERVAL`**: Adjust this value to change how often the health check is performed (in seconds).
- **`HEALTH_CHECK_URL`**: Set this to the URL you want the health check to target.
- **Rate Limiting**: The `/health` endpoint is rate-limited to 1 request per 15 seconds per IP address to prevent abuse.

### 5. Run the Service Locally (Optional)

You can run the Flask service locally to test the health check functionality:

```bash
python health_check.py
```

### 6. Set Up as a Systemd Service

To run the service as a background process and ensure it starts on boot, you can set it up as a `systemd` service.

#### Step 1: Create a systemd service file

Create a new service file:

```bash
sudo nano /etc/systemd/system/health_check.service
```

#### Step 2: Add the following content to the service file

Replace `/path/to/your/project` with the actual path to your project directory:

```ini
[Unit]
Description=Health Check Service
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/path/to/your/project/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 health_check:app
WorkingDirectory=/path/to/your/project
Restart=always
RestartSec=5
User=root
Environment="PATH=/path/to/your/project/venv/bin"
Environment="PYTHONPATH=/path/to/your/project:/path/to/your/project/venv/lib/python3.12/site-packages"

[Install]
WantedBy=multi-user.target
```

#### Step 3: Reload systemd and start the service

Reload systemd to recognize the new service, then start it:

```bash
sudo systemctl daemon-reload
sudo systemctl start health_check.service
```

To enable the service to start on boot:

```bash
sudo systemctl enable health_check.service
```

#### Step 4: Check the status of the service

You can check if the service is running correctly with:

```bash
sudo systemctl status health_check.service
```

### 7. Logs

Logs for the service are written to the system's syslog, which is typically located at `/var/log/syslog`. You can view the logs using:

```bash
sudo tail -f /var/log/syslog
```

The logs will include:
- The result of each health check, including the full JSON response.
- Errors encountered during the health check, along with relevant details.

### 8. API Usage

- **Health Check Endpoint**: The health status and the latest JSON response from the health check can be accessed via the `/health` endpoint. Rate limiting applies, allowing 1 request every 15 seconds per IP address.

```bash
curl http://your-server-address:5000/health
```