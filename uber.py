import json
import logging
from datetime import datetime
from dateutil import parser
import pandas as pd
import aiohttp
import asyncio

from api_requests import make_request
from constants import CONFIG_URL_TEMPLATE, UBER_CFGS_URL_TEMPLATE

def get_uber_token(client, bearer_token):
    url = CONFIG_URL_TEMPLATE.format(client=client)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }
    
    response_data = make_request('GET', url, headers)
    
    if response_data:
        config = response_data.get("data")
        if config:
            uber_token = config.get("INTEGRATIONS", {}).get("UBER", {}).get("server_token")
            if uber_token:
                logging.info("Uber token retrieved successfully.")
                return uber_token
            else:
                logging.error("Uber token not found in the API response.")
        else:
            logging.error("Config data not found in the API response.")
    
    return None

async def fetch_uber_uuid(session, client, store_id, bearer_token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }
    url = UBER_CFGS_URL_TEMPLATE.format(client=client, store_id=store_id)

    try:
        async with session.get(url, headers=headers) as response:
            response_data = await response.json()

            if response_data and "data" in response_data:
                return store_id, response_data["data"][0]["uber_uuid"]
            else:
                logging.error(f"Error fetching data for store {store_id}: {response_data}")
                return store_id, None
    except Exception as e:
        logging.error(f"Request failed for store {store_id}: {e}")
        return store_id, None

async def get_uber_uuids(client, store_ids, bearer_token):
    uber_uuids = {}

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_uber_uuid(session, client, store_id, bearer_token) for store_id in store_ids
        ]
        results = await asyncio.gather(*tasks)

        for store_id, uber_uuid in results:
            if uber_uuid:
                uber_uuids[store_id] = uber_uuid

    return uber_uuids

async def fetch_orders(session, url, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        if response.status == 200:
            return await response.json()
        else:
            logging.error(f"Failed to fetch data: {response.status}")
            return None

async def get_orders_for_store(store_id, uuid, bearer_token, start_time, end_time):
    all_orders = []
    today_date = datetime.utcnow().date()
    url = UBER_ORDERS_URL_TEMPLATE.format(uuid=uuid)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {bearer_token}"
    }

    next_page_token = None

    try:
        async with aiohttp.ClientSession() as session:
            logging.info(f"Fetching order data for store {store_id} from {start_time} to {end_time}")

            while True:
                params = {
                    "start_time": start_time,
                    "end_time": end_time
                }

                # Only add next_page_token if it's not None
                if next_page_token is not None:
                    params["next_page_token"] = next_page_token
                
                response = await fetch_orders(session, url, headers, params)

                if response is None or 'data' not in response or len(response['data']) == 0:
                    break

                # Filter orders that are not for today's date (Uber's API returns in-progress orders despite date range parameter)
                orders = [
                    order for order in response['data']
                    if 'created_time' in order and parser.parse(order['created_time']).date() != today_date
                ]

                all_orders.extend(orders)
                
                # Get the next page token
                next_page_token = response.get("pagination_data", {}).get("next_page_token")
                
                # Break the loop if there's no next page token
                if not next_page_token:
                    break

    except Exception as e:
        logging.error(f"Error occurred during API request for store {store_id}: {e}")

    logging.info(f"Finished fetching orders for store {store_id}. Total orders: {len(all_orders)}")
 
    return all_orders

async def get_uber_orders(uber_uuids, bearer_token, start_time, end_time): 
    tasks = []
    all_orders = []

    for store_id, uuid in uber_uuids.items():
        tasks.append(get_orders_for_store(store_id, uuid, bearer_token, start_time, end_time))

    orders_list = await asyncio.gather(*tasks)

    for orders in orders_list:
        all_orders.extend(orders)

    with open("orders.json", "w") as outfile:
        json.dump(all_orders, outfile, indent=4) 

    return all_orders

def find_missing_orders(all_orders, csv_file_path):
    try:
        processed_orders_df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        print(f"Error: The file {csv_file_path} was not found.")
        return [], 0, 0, 0

    all_orders_df = pd.DataFrame(all_orders)

    processed_ext_ids = processed_orders_df['ext_id'].values

    missing_orders_df = all_orders_df[~all_orders_df['id'].isin(processed_ext_ids)]

    missing_orders = missing_orders_df.to_dict(orient='records')

    total_orders = len(all_orders)
    missing_orders_count = len(missing_orders)
    failure_rate = (missing_orders_count / total_orders) * 100 if total_orders > 0 else 0

    return missing_orders, total_orders, missing_orders_count, failure_rate