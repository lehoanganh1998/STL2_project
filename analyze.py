import datetime
import pandas as pd
import time
import requests
from tqdm import tqdm
import os
import csv

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

# Define thresholds
min_wallets = 3
vendor_addresses = {}

# Iterate through each Bitcoin address
for address in tqdm(btc_addresses):
    try:
        # Fetch transaction data for the current address
        data = fetch_address_data(address)

        # Find potential vendor addresses
        potential_vendor_addresses = set()
        for tx in data:
            if 'vin' in tx and tx['vin'][0]['prevout']['scriptpubkey_address'] == address:
                for vout in tx['vout']:
                    potential_vendor_addresses.add(vout['scriptpubkey_address'])

        # Check potential vendor addresses
        best_vendor_address = None
        best_vendor_wallet_count = 0
        for potential_vendor_address in potential_vendor_addresses:
            vendor_data = fetch_address_data(potential_vendor_address)
            vendor_wallet_count = len(set([tx['vin'][0]['prevout']['scriptpubkey_address'] for tx in vendor_data if 'vin' in tx]))
            if vendor_wallet_count >= min_wallets and vendor_wallet_count > best_vendor_wallet_count:
                best_vendor_address = potential_vendor_address
                best_vendor_wallet_count = vendor_wallet_count

        # Add the best candidate vendor address to the dictionary
        if best_vendor_address is not None:
            if best_vendor_address not in vendor_addresses:
                vendor_addresses[best_vendor_address] = 1
            else:
                vendor_addresses[best_vendor_address] += 1
        time.sleep(delay_seconds)
    except KeyboardInterrupt:
        break

# Filter vendor addresses by wallet count
filtered_vendor_addresses = {k: v for k, v in vendor_addresses.items() if v >= min_wallets}

# Output vendor addresses and wallet counts to CSV file
with open("vendor_wallet_counts.csv", mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Vendor Address", "Wallet Count"])
    for vendor_address, wallet_count in filtered_vendor_addresses.items():
        writer.writerow([vendor_address, wallet_count])

print("Vendor wallet counts written to vendor_wallet_counts.csv")