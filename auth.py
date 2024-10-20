import logging
from api_requests import make_request
from constants import AUTH_URL

def polygon_central_login(client:str, username: str, password: str) -> str:
    url = AUTH_URL.format(client=client)

    payload = {
        "username": username,
        "psw": password,
        "auth_type": "U"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    response_data = make_request('POST', url, headers, payload)
    
    if response_data:
        token = response_data.get("token")
        if token:
            logging.info("Bearer token retrieved successfully.")
            return token
        else:
            logging.error("Bearer token not found in response.")
    return None
