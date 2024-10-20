import logging
import asyncio
import sys
from itertools import cycle
from dotenv import load_dotenv

from auth import polygon_central_login
from uber import get_uber_token, get_uber_uuids, get_uber_orders, find_missing_orders

load_dotenv()

logging.basicConfig(
    filename='script.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Spinner function to display loading indicator
async def spinner():
    spinner_chars = cycle(['|', '/', '-', '\\'])
    while True:
        sys.stdout.write(f"\rProcessing... {next(spinner_chars)}")
        sys.stdout.flush()
        await asyncio.sleep(0.1) # Spinner speed

async def main():
    # Starting spinner in the background
    spinner_task = asyncio.create_task(spinner())

    try:
        # Step 1: Logging script details
        logging.info(f"--- New Script Run Started for Client: {client_name} ---")
        logging.info(f"Fetching orders for Store IDs: {store_ids}")
        logging.info(f"Fetching orders from Start Time: {start_time} to End Time: {end_time}")

        # Step 2: Fetching bearer token from Polygon Central
        token = polygon_central_login(client_name, username, password)
        if not token:
            logging.error("Failed to retrieve bearer token.")
            return

        # Step 3: Fetching Uber token
        uber_token = get_uber_token(client_name, token)
        if not uber_token:
            logging.error("Failed to retrieve Uber token.")
            return

        logging.info(f"Uber Token successfully retrieved: {uber_token}")

        # Step 4: Fetching Uber UUIDs for the listed stores
        uber_uuids = await get_uber_uuids(client_name, store_ids, token)
        if not uber_uuids:
            logging.error("Failed to retrieve Uber UUIDs.")
            return 

        logging.info(f"Uber UUIDs retrieved: {uber_uuids}")

        # Step 5: Fetching Uber orders
        all_orders = await get_uber_orders(uber_uuids, uber_token, start_time, end_time)
        if not all_orders:
            logging.error("No orders found or failed to retrieve orders.")
            return

        logging.info(f"Retrieved {len(all_orders)} orders from Uber.")

        # Step 6: Compare Uber orders with processed Polygon Central orders CSV
        csv_file_path = "./processed_orders.csv"
        missing_orders, total_orders, missing_orders_count, failure_rate = find_missing_orders(all_orders, csv_file_path)

        # Logging results
        if missing_orders:
            order_ids = [order['id'] for order in missing_orders]
            logging.info(f"Missing Order IDs: {order_ids}")
        else:
            logging.info("No missing orders found.")

        logging.info(f"Total Orders: {total_orders}")
        logging.info(f"Missing Orders Count: {missing_orders_count}")
        logging.info(f"Failure Rate: {failure_rate:.2f}%")

        # End of script
        logging.info(f"--- Script Run Completed for Client: {client_name} ---\n")

    finally:
        # Cancelling spinner task and printing completion 
        spinner_task.cancel()
        sys.stdout.write("\rProcessing complete!          \n")
        sys.stdout.flush()

if __name__ == "__main__":
    username = os.getenv("POLYGON_CENTRAL_USERNAME")
    password = os.getenv("POLYGON_CENTRAL_PASSWORD")
    client_name = ""
    store_ids = []
    start_time = ""
    end_time = ""

    asyncio.run(main())