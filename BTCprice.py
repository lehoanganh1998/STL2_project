import datetime
import pandas as pd
import time
import requests
from tqdm import tqdm
import os
import statistics
import pprint

addresses_df = pd.read_csv("dataset/addresses.csv")
btc_addresses = addresses_df['account'].tolist()

delay_seconds = 0.1   # Delay between requests in seconds for the limit
features = []

def fetch_address_data(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Unable to fetch data for address {address}")

def fetch_btc_price(date):
    url = f"https://api.coindesk.com/v1/bpi/historical/close.json?start={date}&end={date}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bpi'][date]
    else:
        raise ValueError("Unable to fetch Bitcoin price")

for address in tqdm(btc_addresses):
    try:
        data = fetch_address_data(address)

        first_seen = datetime.datetime.fromtimestamp(data[0]['status']['block_time'])
        last_seen = datetime.datetime.fromtimestamp(data[-1]['status']['block_time'])
        lifetime = abs((last_seen - first_seen).days)

        total_received_usd = 0
        total_sent_usd = 0
        total_usd = 0

        for tx in data:
            tx_time = datetime.datetime.fromtimestamp(tx['status']['block_time'])
            btc_price = fetch_btc_price(tx_time.strftime('%Y-%m-%d'))

            received_btc = tx['vin'][0]['prevout']['value'] / 10**8
            sent_btc = tx['vout'][0]['value'] / 10**8
            total_btc = received_btc - sent_btc

            received_usd = received_btc * btc_price
            sent_usd = sent_btc * btc_price
            total_usd += total_btc * btc_price

            total_received_usd += received_usd
            total_sent_usd += sent_usd

        features.append((address, first_seen, lifetime, total_received_usd, total_sent_usd, total_usd))
        time.sleep(delay_seconds)
    except KeyboardInterrupt:
        break

# Update the columns list with the new features
columns=['address', 'first_seen', 'lifetime', 'total_received_usd', 'total_sent_usd', 'total_usd']
df = pd.DataFrame(features, columns=columns)

# Save the DataFrame to a CSV file
output_folder = "./result"
os.makedirs(output_folder, exist_ok=True)
output_name = "addresses_price.csv"
output_file = os.path.join(output_folder, output_name)
df.to_csv(output_file, index=False)
