import csv

# Define minimum number of wallets for identifying potential vendors
min_wallets = 3

# Read in vendor addresses and wallet counts from CSV file
vendor_addresses = {}
with open("Vendor_results.csv", mode="r") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # skip header row
    for row in reader:
        vendor_address = row[0]
        wallet_count = int(row[1])
        vendor_addresses[vendor_address] = wallet_count

# Divide vendor addresses into types based on wallet count
vendor_type_counts = {"Small": 0, "Medium": 0, "Large": 0}
for vendor_address, wallet_count in vendor_addresses.items():
    if wallet_count < 10:
        vendor_type_counts["Small"] += 1
    elif wallet_count < 20:
        vendor_type_counts["Medium"] += 1
    else:
        vendor_type_counts["Large"] += 1

# Output vendor type counts to CSV file
with open("vendor_type_counts.csv", mode="w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Vendor Type", "Count"])
    for vendor_type, count in vendor_type_counts.items():
        writer.writerow([vendor_type, count])

print("Vendor type counts written to vendor_type_counts.csv")