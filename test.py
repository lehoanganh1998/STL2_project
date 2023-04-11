import datetime
import pandas as pd
import time
import requests
from tqdm import tqdm
import os

# BATCH NUMBER
batch_num = 1
# data import
dataset_folder = "./dataset"
folder_list = os.listdir(dataset_folder)

# dataset list create
datasets = []
for file in folder_list:
    if "batch" in file and str(batch_num) in file:
        dataset_loc = os.path.join(dataset_folder, file)
        addresses_df = pd.read_csv(dataset_loc)
        btc_addresses = addresses_df['account'].tolist()

delay_seconds = 10  # Delay between requests in seconds for the limit
features = []

def fetch_address_data(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Unable to fetch data for address {address}")

for address in tqdm(btc_addresses):
    data = fetch_address_data(address)
    first_seen = datetime.datetime.fromtimestamp(data[0]['status']['block_time'])
    last_seen = datetime.datetime.fromtimestamp(data[-1]['status']['block_time'])
    lifetime = abs((last_seen - first_seen).days)
    active_days = len(set([datetime.datetime.fromtimestamp(tx['status']['block_time']).strftime('%Y-%m-%d') for tx in data]))

    incoming_amount = 0
    outgoing_amount = 0
    incoming_tx_count = 0
    outgoing_tx_count = 0

    for tx in data:
        is_incoming_tx = False
        is_outgoing_tx = False

        for vin in tx['vin']:
            if vin['prevout']['scriptpubkey_address'] == address:
                outgoing_amount += vin['prevout']['value']
                is_outgoing_tx = True

        for vout in tx['vout']:
            if vout['scriptpubkey_address'] == address:
                incoming_amount += vout['value']
                is_incoming_tx = True

        incoming_tx_count += is_incoming_tx
        outgoing_tx_count += is_outgoing_tx

    features.append((address, lifetime, active_days, incoming_amount, outgoing_amount, incoming_tx_count, outgoing_tx_count))
    time.sleep(delay_seconds)  # Add delay between requests

df = pd.DataFrame(features, columns=['address', 'lifetime', 'active_days', 'incoming_amount', 'outgoing_amount', 'incoming_tx_count', 'outgoing_tx_count'])

# Save the DataFrame to a CSV file
output_folder = "./result"
os.makedirs(output_folder, exist_ok=True)
output_name = "result_batch_{}".format(batch_num)
output_file = os.path.join(output_folder, output_name)
df.to_csv(output_file, index=False)
