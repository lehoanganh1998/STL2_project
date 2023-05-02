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
    
for address in tqdm(btc_addresses):
    try:
        data = fetch_address_data(address)
        first_seen = datetime.datetime.fromtimestamp(data[0]['status']['block_time'])
        last_seen = datetime.datetime.fromtimestamp(data[-1]['status']['block_time'])
        lifetime = abs((last_seen - first_seen).days)
        active_days = len(set([datetime.datetime.fromtimestamp(tx['status']['block_time']).strftime('%Y-%m-%d') for tx in data]))

        incoming_amount = 0
        outgoing_amount = 0
        incoming_tx_count = 0
        outgoing_tx_count = 0
        transaction_values = []
        transaction_fees = []
        unique_addresses = set()
        
        for tx in data:
            is_incoming_tx = False
            is_outgoing_tx = False

            for vin in tx['vin']:
                if vin['prevout']['scriptpubkey_address'] == address:
                    outgoing_amount += vin['prevout']['value']
                    outgoing_tx_count += 1
                    is_outgoing_tx = True
                    transaction_values.append(vin['prevout']['value'] - tx['vout'][0]['value'])

                    unique_addresses.add(tx['vout'][0]['scriptpubkey_address'])

            for vout in tx['vout']:
                if vout['scriptpubkey_address'] == address:
                    incoming_amount += vout['value']
                    incoming_tx_count += 1
                    is_incoming_tx = True
                    transaction_fees.append(tx['fee'])

                    unique_addresses.add(vin['prevout']['scriptpubkey_address'])

            incoming_tx_count += is_incoming_tx
            outgoing_tx_count += is_outgoing_tx

        avg_transaction_value = sum(transaction_values) / len(transaction_values) if transaction_values else 0
        largest_transaction_value = max(transaction_values) if transaction_values else 0
        smallest_transaction_value = min(transaction_values) if transaction_values else 0

        incoming_transaction_volume = incoming_amount
        outgoing_transaction_volume = outgoing_amount
        transaction_frequency = (incoming_tx_count + outgoing_tx_count) / lifetime
        incoming_outgoing_ratio = incoming_tx_count / outgoing_tx_count if outgoing_tx_count > 0 else incoming_tx_count
        avg_transaction_fee = sum(transaction_fees) / len(transaction_fees) if transaction_fees else 0
        largest_transaction_fee = max(transaction_fees) if transaction_fees else 0
        smallest_transaction_fee = min(transaction_fees) if transaction_fees else 0

        unique_address_count = len(unique_addresses)
        
        features.append((address, first_seen,lifetime, active_days, incoming_amount, outgoing_amount, incoming_tx_count, outgoing_tx_count, avg_transaction_value, largest_transaction_value, smallest_transaction_value, incoming_transaction_volume, outgoing_transaction_volume, transaction_frequency, incoming_outgoing_ratio, avg_transaction_fee, largest_transaction_fee, smallest_transaction_fee, unique_address_count))
        time.sleep(delay_seconds)
    except KeyboardInterrupt:
        break

# Update the columns list with the new features
columns=['address', 'first_seen','lifetime', 'active_days', 'incoming_amount', 'outgoing_amount', 'incoming_tx_count', 'outgoing_tx_count', 'avg_transaction_value', 'largest_transaction_value', 'smallest_transaction_value', 'incoming_transaction_volume', 'outgoing_transaction_volume', 'transaction_frequency', 'incoming_outgoing_ratio', 'avg_transaction_fee', 'largest_transaction_fee', 'smallest_transaction_fee', 'unique_address_count']
df = pd.DataFrame(features, columns=columns)

# Save the DataFrame to a CSV file
output_folder = "./result"
os.makedirs(output_folder, exist_ok=True)
# output_name = "result_batch_{}.csv".format(batch_num)
output_name = "addresses_results.csv"
output_file = os.path.join(output_folder, output_name)
df.to_csv(output_file, index=False)