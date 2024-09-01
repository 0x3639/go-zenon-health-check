import threading
import time
import requests
import json
import logging
from flask import Flask, jsonify
import logging.handlers
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

# Configure logging to syslog
syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
formatter = logging.Formatter('%(name)s: %(levelname)s %(message)s')
syslog_handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(syslog_handler)

# Configure rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["1 per 15 seconds"]  # Limit requests to 1 per 15 seconds per IP
)

# Configuration
CHECK_INTERVAL = 60  # Health check interval in seconds
HEALTH_CHECK_URL = "http://127.0.0.1:35997"  # URL for the health check

# Health check status and last response
health_status = 500  # Default to server error until the first check is performed
last_response_json = {}  # Stores the last JSON response from the health check

def run_health_check():
    global health_status, last_response_json
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "id": 40,
        "method": "stats.syncInfo",
        "params": []
    }

    try:
        response = requests.post(HEALTH_CHECK_URL, headers=headers, json=payload, timeout=5)
        response.raise_for_status()  # Ensure we capture any HTTP errors

        response_json = response.json()
        last_response_json = response_json  # Store the last successful JSON response
        state = response_json["result"]["state"]

        logger.info(f"Health check result: {json.dumps(response_json)}")  # Log the JSON result

        if state in [2, 3]:
            health_status = 200
        elif state == 1:
            health_status = 500
            logger.error(f"Health check failed with state: {state}, JSON: {json.dumps(response_json)}")
        else:
            health_status = 500
            logger.error(f"Unknown state encountered: {state}, JSON: {json.dumps(response_json)}")

    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        logger.error(f"Error during health check: {e}")
        health_status = 500
        last_response_json = {"error": str(e)}

def start_periodic_health_check():
    while True:
        run_health_check()
        time.sleep(CHECK_INTERVAL)  # Wait for the specified interval before the next check

# Start the background thread for periodic health checks
threading.Thread(target=start_periodic_health_check, daemon=True).start()

@app.route('/health', methods=['GET'])
@limiter.limit("1 per 15 seconds")
def health():
    return jsonify(last_response_json), health_status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
