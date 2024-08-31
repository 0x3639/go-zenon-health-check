import requests
import json
import logging
from flask import Flask, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(filename='health_check.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# Health check status
health_status = 500  # Default to server error until the first check is performed

def run_health_check():
    global health_status
    url = "http://127.0.0.1:35997"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "jsonrpc": "2.0",
        "id": 40,
        "method": "stats.syncInfo",
        "params": []
    }

    try:
        # Send the POST request with a 5-second timeout
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        # Parse the JSON response
        response_json = response.json()
        state = response_json["result"]["state"]
        
        # Set health status based on the state
        if state in [2, 3]:
            health_status = 200
            logging.info(f"Health check passed with state: {state}")
        elif state == 1:
            health_status = 500
            logging.error(f"Health check failed with state: {state}")
        else:
            health_status = 500
            logging.error(f"Unknown state encountered: {state}")

    except requests.exceptions.Timeout:
        logging.error("Health check timed out after 5 seconds")
        health_status = 500  # Return server error if the request times out

    except requests.exceptions.RequestException as e:
        logging.error(f"Error during health check: {e}")
        health_status = 500  # Default to server error if any exception occurs

@app.route('/health', methods=['GET'])
def health():
    return '', health_status

if __name__ == '__main__':
    from threading import Timer

    def run_periodic_health_check():
        run_health_check()
        Timer(60, run_periodic_health_check).start()

    run_periodic_health_check()

    # Start the Flask app with Gunicorn if running directly
    app.run(host='0.0.0.0', port=5000)
