import pandas as pd

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('result/vendor_list.csv')

# Group the data by the 'Num Unique Senders' column and count the number of entries for each group
grouped = df.groupby('Num Unique Senders')['Vendor Address'].count()

# Calculate the number of vendor addresses for the three ranges of unique senders
num_addresses_6_to_15 = grouped.loc[6:15].sum()
num_addresses_16_to_45 = grouped.loc[16:45].sum()
num_addresses_other = grouped.loc[~grouped.index.isin(range(6, 16)) & ~grouped.index.isin(range(16, 46))].sum()

# Print out the results
print(f"Number of vendor addresses for 6-15 unique senders: {num_addresses_6_to_15}")
print(f"Number of vendor addresses for 16-35 unique senders: {num_addresses_16_to_45}")
print(f"Number of vendor addresses for 36-153 unique senders: {num_addresses_other}")
