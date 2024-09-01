
# Health Check Service

This Python service runs a health check by making a POST request to a specified endpoint every minute and provides a health status via an HTTP API.

## Features

- Periodic health checks (every 60 seconds)
- Returns HTTP 200 if the service is healthy, 500 if it is not
- Error logging for timeouts and failed requests
- Runs as a Flask web service

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

### 4. Run the Service Locally (Optional)

You can run the Flask service locally to test the health check functionality:

```bash
python health_check.py
```

### 5. Set Up as a Systemd Service

To run the service as a background process and ensure it starts on boot, you can set it up as a `systemd` service.

#### Step 1: Create a systemd service file

Create a new service file:

```bash
sudo nano /etc/systemd/system/health_check.service
```

#### Step 2: Add the following content to the service file

Replace `/path/to/your/project` with the actual path to your project directory and `your-username` with your actual username:

```ini
[Unit]
Description=Health Check Service
After=network.target

[Service]
ExecStart=/path/to/your/project/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 health_check:app
WorkingDirectory=/path/to/your/project
Restart=always
RestartSec=5
User=your-username
Environment="PATH=/path/to/your/project/venv/bin"

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

### 6. Logs

Logs for the service are written to the system's syslog, which is typically located at `/var/log/syslog`. You can view the logs using:

```bash
sudo tail -f /var/log/syslog
```

The logs will include:
- The result of each health check, including the full JSON response.
- Errors encountered during the health check, along with relevant details.

### 7. API Usage

- **Health Check Endpoint**: The health status and the latest JSON response from the health check can be accessed via the `/health` endpoint.

```bash
curl http://your-server-address:5000/health
```