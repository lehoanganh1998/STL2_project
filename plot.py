import pandas as pd
import matplotlib.pyplot as plt

# Read the CSV file into a pandas DataFrame
df = pd.read_csv('result/addresses_updated_price.csv')


# Create a new pandas Series with the desired y-values
# Round the 'total_sent_usd' column to 2 decimal places
df['total_sent_usd'] = df['total_sent_usd'].round(2)
print(max(df['total_sent_usd']))
exit()
# Create a line plot of the 'total_sent_usd' column with the index as the x-axis
plt.plot(df.index, df['total_sent_usd'])

# Add a title and labels to the plot
plt.title('Total sent USD')
plt.xlabel('Address Index')
plt.ylabel('Total sent USD')


# Display the plot
plt.savefig('your_plot.png')
