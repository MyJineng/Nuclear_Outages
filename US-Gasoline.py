import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
from eia_key import key
# Retrieve data from EIA API and convert from JSON to Pandas DataFrame
NUC_OUT = f"https://api.eia.gov/v2/nuclear-outages/us-nuclear-outages/data/?frequency=daily&data[0]=capacity&data[1]=outage&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={key}"
NG_PRC = f'https://api.eia.gov/v2/natural-gas/sum/lsum/data/?frequency=monthly&data[0]=value&facets[series][]=N3045US3&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=5000&api_key={key}'
response = requests.get(NUC_OUT)
response2 = requests.get(NG_PRC)
df2 = pd.DataFrame(response2.json()['response']['data'])
# Reformat Datetime to merge natural gas price series with Nuclear Outages dataframe
df2['period'] = pd.to_datetime(df2['period'], format='%Y-%m')
df2.set_index('period', inplace=True)
df2.index = df2.index.to_period('M')
df = pd.DataFrame(response.json()['response']['data'])
# Reformat Datetime to prepare for merge and sum daily data into monthly
df['period'] = pd.to_datetime(df['period'])
df.set_index('period', inplace=True)
df['outage'] = pd.to_numeric(df['outage'])
df['capacity'] = pd.to_numeric(df['capacity'])
dfm = df[:1500].resample('M').sum()
dfm.index = dfm.index.to_period('M')
# Merge data
dfm = pd.merge(dfm, df2, on='period', how='inner')
monthly_data = dfm
monthly_data['value'] = pd.to_numeric(monthly_data['value'], errors='coerce')
print(monthly_data)

spearman_corr = (monthly_data['outage'] / monthly_data['capacity']).corr(monthly_data['value'], method='spearman')
print(f'Spearman correlation: {spearman_corr.round(2)}')
pearson_corr = (monthly_data['outage'] / monthly_data['capacity']).corr(monthly_data['value'], method='pearson')
print(f'Pearson correlation: {pearson_corr.round(2)}')


x_values = monthly_data.index.astype(str)

# Create a new figure and axis
fig, ax1 = plt.subplots()

# Plot the outage percentage on the left y-axis
ax1.plot(x_values, ((monthly_data['outage'] / monthly_data['capacity']) * 100),
         marker='o', linestyle='-', color='b', label='Outage Percentage')
ax1.set_xlabel('Month')
ax1.set_ylabel('Nuclear Outage as Percent of Total Capacity (%)', color='b')
ax1.tick_params(axis='y', labelcolor='b')

# Create a second y-axis for the price
ax2 = ax1.twinx()
ax2.plot(x_values, monthly_data['value'],
         marker='s', linestyle='--', color='r', label='Price')
ax2.set_ylabel('Natural Gas Price ($/MCF)', color='r')
ax2.tick_params(axis='y', labelcolor='r')

# Set x-ticks with diagonal labels
ax1.set_xticks(x_values)  # Set ticks at each value in x_values
ax1.set_xticklabels(x_values, rotation=45, ha='right')  # Rotate and align labels

# Add title and legends
plt.title('US Nuclear Outages vs Natural Gas Prices')

# Show the plot
plt.tight_layout()  # Adjust layout for better fit
plt.show()