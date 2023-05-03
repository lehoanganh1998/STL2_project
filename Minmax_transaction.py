import datetime
import pandas as pd
import time
import requests
from tqdm import tqdm
import os
import statistics
import pprint

# read the csv file into a pandas dataframe
df = pd.read_csv("result/addresses_price.csv")

# find the row with the highest total_received_usd value
max_received_row = df.loc[df["total_received_usd"].idxmax()]

# find the row with the highest total_sent_usd value
max_sent_row = df.loc[df["total_sent_usd"].idxmax()]

# get the address for each row
max_received_address = max_received_row["address"]
max_sent_address = max_sent_row["address"]

# create a list of the two addresses
btc_addresses = [max_received_address, max_sent_address]

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


# find the row with the highest total_received_usd value
max_received_row = df.loc[df["total_received_usd"].idxmax()]

# find the row with the highest total_sent_usd value
max_sent_row = df.loc[df["total_sent_usd"].idxmax()]

# get the address for each row
max_received_address = max_received_row["address"]
max_sent_address = max_sent_row["address"]

# create a dictionary of the two addresses with transaction details
btc_transactions = {}

for address in tqdm([max_received_address, max_sent_address]):
    try:
        data = fetch_address_data(address)

        transactions = {}

        for tx in data:
            tx_time = datetime.datetime.fromtimestamp(tx['status']['block_time'])
            btc_price = fetch_btc_price(tx_time.strftime('%Y-%m-%d'))

            received_btc = tx['vin'][0]['prevout']['value'] / 10**8
            sent_btc = tx['vout'][0]['value'] / 10**8
            total_btc = received_btc - sent_btc

            received_usd = received_btc * btc_price
            sent_usd = sent_btc * btc_price

            if address == max_received_address:
                # only include received value for the address with the highest received value
                transactions[tx_time.strftime('%Y-%m-%d')] = {"received": received_usd}
            elif address == max_sent_address:
                # only include sent value for the address with the highest sent value
                transactions[tx_time.strftime('%Y-%m-%d')] = {"sent": sent_usd}
            else:
                # include both sent and received values for other addresses
                transactions[tx_time.strftime('%Y-%m-%d')] = {"received": received_usd, "sent": sent_usd}

        btc_transactions[address] = transactions
        time.sleep(delay_seconds)
    except KeyboardInterrupt:
        break

# print the transaction details for each address
for address, transactions in btc_transactions.items():
    print(address)
    pprint.pprint(transactions)