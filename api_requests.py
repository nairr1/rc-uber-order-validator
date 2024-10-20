import requests
import logging
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def make_request(method: str, url: str, headers: dict, payload=None):
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=payload)
        elif method == 'GET':
            response = requests.get(url, headers=headers, params=payload)
        else:
            raise ValueError("Invalid request method.")
        
        response.raise_for_status()
        return response.json()
    except (HTTPError, ConnectionError, Timeout, RequestException) as req_err:
        logging.error(f"Request error for URL {url}: {req_err}")
    except Exception as err:
        logging.error(f"Unexpected error for URL {url}: {err}")
    
    return None
