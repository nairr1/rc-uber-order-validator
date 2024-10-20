# Redcat Uber Order Validator 

This script is designed to retrieve Uber orders using store UUIDs from Polygon Central and an Uber authentication token. It compares the retrieved Uber orders with the processed order IDs stored in `processed_orders.csv`. The script generates a `orders.json` file with order data, logs essential information such as order counts, missing orders, and failure rates, and stores detailed logs in `script.log`.

## Features

- Fetches Uber authentication token.
- Retrieves store UUIDs from Polygon Central.
- Retrieves orders from Uber API using the store UUIDs and the Uber auth token.
- Compares retrieved Uber orders with those in the `processed_orders.csv` file.
- Outputs missing order IDs and calculates the failure rate.
- Logs relevant API responses, errors, and information into `script.log`.
  
## Prerequisites

Ensure the following modules are installed before running the script:

```bash
pip install requests aiohttp python-dotenv pandas python-dateutil
```

## Setup

1. Clone the repository:

```bash
git clone https://github.com/nairr1/rc-uber-order-validator.git
cd rc-uber-order-validator
```

2. Create and populate the `.env` file with the required Polygon Central credentials:
```plaintext
POLYGON_CENTRAL_USERNAME=your_polygon_central_username
POLYGON_CENTRAL_PASSWORD=your_polygon_central_password
```

3. In the `constants.py` file, fill out the following constants:
```python
AUTH_URL = 'your_auth_url'
CONFIG_URL_TEMPLATE = 'your_polygon_central_config_url'
UBER_CFGS_URL_TEMPLATE = 'your_uber_cfgs_url'
UBER_ORDERS_URL_TEMPLATE = 'your_uber_orders_url'
```

4. In `main.py`, fill in the following variables before running the script:
```python
client_name = 'your_client_polygon_central_url_name'  # Example: "yourclientname.polygoncentral.com"
store_ids = ['store_id_1', 'store_id_2', ...]  # List of store UUIDs
start_time = '2024-10-12T00:00:00Z'  # Example: ISO 8601 format timestamp
end_time = '2024-10-12T23:59:59Z'  # Example: ISO 8601 format timestamp
```

## How to Run

1. After setting up the required values in `.env`, `constants.py`, and `main.py`, you can run the script as follows:
```bash
python main.py
```

2. Ensure that a `processed_orders.csv` file is present in the same directory. This file should contain the list of processed Uber order IDs pulled from the Polygon Central database.

## Output

1. `orders.json`: A file that contains the retrieved Uber orders in JSON format.

2. `script.log`: A log file that contains:
- Number of Uber orders retrieved.
- Number of orders missing from the `processed_orders.csv` list.
- Missing order IDs.
- Failure rate (calculated as the percentage of missing orders).
- Responses and errors from the Uber & Polygon Central API, including any HTTP error, timeouts, or connection issues.

## Required Libraries

The script relies on the following Python modules:

- `requests`: For making HTTP requests to Uber and Polygon Central APIs.
- `aiohttp`: For asynchronous HTTP requests.
- `asyncio`: For running asynchronous operations.
- `logging`: For creating log entries in `script.log`.
- `dotenv`: For loading environment variables from `.env`.
- `pandas`: For handling CSV data (`processed_orders.csv`).
- `python-dateutil`: For parsing and manipulating date and time values.
- `json`: For handling JSON data.