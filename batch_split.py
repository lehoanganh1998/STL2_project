import pandas as pd
from tqdm import tqdm

# Read the addresses from the original CSV file
input_filename = 'addresses.csv'
addresses_df = pd.read_csv(input_filename)

# Set the batch size
batch_size = 1900

# Calculate the number of batches
num_batches = (len(addresses_df) + batch_size - 1) // batch_size

# Split the addresses into smaller batches and save them as separate CSV files
for i in tqdm(range(num_batches)):
    start_index = i * batch_size
    end_index = min((i + 1) * batch_size, len(addresses_df))
    batch_df = addresses_df[start_index:end_index]
    batch_filename = f'addresses_batch_{i + 1}.csv'
    batch_df.to_csv(batch_filename, index=False)

print(f'Split {len(addresses_df)} addresses into {num_batches} batches of {batch_size} addresses each.')
