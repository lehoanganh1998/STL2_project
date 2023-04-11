import blockcypher
import datetime
import pandas as pd
import time
from tqdm import tqdm
import os

#! BATCH NUMBER
batch_num = 1
# data import
dataset_folder = "/home/lee/STL project/dataset"
folder_list = os.listdir(dataset_folder)

# dataset list create
datasets = []
for file in folder_list:
    if "batch" in file and str(batch_num) in file:
        dataset_loc = os.path.join(dataset_folder, file)
        addresses_df = pd.read_csv(dataset_loc)
        btc_addresses = addresses_df['account'].tolist()

delay_seconds = 25  # Delay between requests in seconds for the limit
features = []

for address in tqdm(btc_addresses):
    data = blockcypher.get_address_details(address,api_key="a8af2661a5e34021a064aee76e3790f4")
    first_seen = data['txrefs'][0]['confirmed']
    last_seen = data['txrefs'][-1]['confirmed']
    lifetime = abs((last_seen - first_seen).days)
    active_days = len(set([txref['confirmed'].strftime('%Y-%m-%d') for txref in data['txrefs']]))
    incoming_amount = sum([txref['value'] for txref in data['txrefs'] if txref['tx_input_n'] == -1])
    outgoing_amount = sum([txref['value'] for txref in data['txrefs'] if txref['tx_output_n'] == -1])
    incoming_tx_count = sum([1 for txref in data['txrefs'] if txref['tx_input_n'] == -1])
    outgoing_tx_count = sum([1 for txref in data['txrefs'] if txref['tx_output_n'] == -1])

    features.append((address, lifetime, active_days, incoming_amount, outgoing_amount, incoming_tx_count, outgoing_tx_count))
    
    time.sleep(delay_seconds)  # Add delay between requests

df = pd.DataFrame(features, columns=['address', 'lifetime', 'active_days', 'incoming_amount', 'outgoing_amount', 'incoming_tx_count', 'outgoing_tx_count'])

# Save the DataFrame to a CSV file
output_folder = "/home/lee/STL project/result"
output_name = "result_batch_" + batch_num
output_file = os.path.join(output_folder,output_name)
df.to_csv(output_file, index=False)

