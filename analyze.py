import datetime
import pandas as pd
import time
import requests
import os
import csv
from tqdm import tqdm
addresses_df = pd.read_csv("dataset/addresses.csv")
btc_addresses = addresses_df['account'].tolist()

delay_seconds = 0.1   # Delay between requests in seconds for the limit
vendor_addresses = []
threshold = 5
def fetch_address_data(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Unable to fetch data for address {address}")

# Iterate through each Bitcoin address
for address in tqdm(btc_addresses):
    try:
        # Fetch transaction data for the current address
        data = fetch_address_data(address)

        # Check potential vendor addresses
        is_vendor = False
        sender_all = set()
        sender_in = set()
        for tx in data:
            if len(tx.get('vin', [])) > 0 and len(tx.get('vout', [])) > 0:
                sender_addresses = set([vin['prevout']['scriptpubkey_address'] for vin in tx['vin']])
                receiver_addresses = set([vout['scriptpubkey_address'] for vout in tx['vout']])
                if address in receiver_addresses:
                    sender_in.update(sender_addresses)
                sender_all.update(sender_addresses)

        unique_sender_out = sender_all - sender_in
        
        if len(unique_sender_out) > threshold and len(sender_all.intersection(sender_in)) > 0:
            intersection_wallet = sender_all.intersection(sender_in).pop() if len(sender_all.intersection(sender_in)) > 0 else None
            vendor_addresses.append((address, len(unique_sender_out), intersection_wallet))

        time.sleep(delay_seconds)
    except KeyboardInterrupt:
        break

# Output vendor addresses to CSV file
with open("vendor_addresses.csv", mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Vendor Address", "Num Unique Senders", "Intersection Wallet"])
    for vendor_address in vendor_addresses:
        writer.writerow([vendor_address[0], vendor_address[1], vendor_address[2]])

print("Vendor addresses written to vendor_addresses.csv.")