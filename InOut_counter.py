import requests
from pprint import pprint
BTC_ADDRESS = '3LEDrj6ueaf6J6jYd3LiX9yMiVuYeftuoe'

# Step 1: Get transaction history

def fetch_address_data(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Unable to fetch data for address {address}")

def fetch_address_transaction(tx):
    url = f"https://blockstream.info/api/tx/{tx}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Unable to fetch data for address {tx}")
# Count outgoing transactions
data = fetch_address_data(BTC_ADDRESS)
num_outgoing_transactions_receiver = 0
num_incoming_transactions_sender = 0
in_transactions = []
out_transactions = []
for tx in data:
    if any(vin["prevout"]["scriptpubkey_address"] == BTC_ADDRESS for vin in tx["vin"]):
        in_transactions.append(tx['txid'])
    if tx['txid'] not in in_transactions:
        out_transactions.append(tx['txid'])
        
for tx in out_transactions:
    transactions  = fetch_address_transaction(tx)
    for a in transactions['vout']:
        num_outgoing_transactions_receiver += 1


for tx in in_transactions:
    transactions  = fetch_address_transaction(tx)
    for a in transactions['vout']:
        num_incoming_transactions_sender += 1
print("Address: ", BTC_ADDRESS)
print("Number of receiver in outgoing transactions: ", num_outgoing_transactions_receiver)
print("Number of sender in incoming transactions: ", num_incoming_transactions_sender)