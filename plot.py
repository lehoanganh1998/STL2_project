import matplotlib.pyplot as plt
import pandas as pd
import os

import pandas as pd
import seaborn as sns

# Read in the results file and create a DataFrame
df = pd.read_csv("addresses_results.csv")

df['first_seen'] = pd.to_datetime(df['first_seen'])
df = df.sort_values(by='first_seen')
x = df['first_seen']
y = df['unique_address_count']

# Create the line chart
plt.plot(x, y)
plt.xlabel('Date')
plt.ylabel('Number of unique addresses')
plt.title('Line chart of unique addresses over time')

# Save the plot to a file
output_folder = "./plots"
os.makedirs(output_folder, exist_ok=True)
output_name = "unique_addresses_over_time_linechart.png"
output_file = os.path.join(output_folder, output_name)
plt.savefig(output_file)