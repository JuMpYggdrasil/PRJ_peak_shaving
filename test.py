import csv
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

timestamp_interval = 15/60 # minute

# Load data from a CSV file
timestamps = []
load_data = []

with open('load_data_cleaned.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row if present
    for row in reader:
        # Assuming the first column is timestamp in 'dd.mm.yyyy HH:MM' format
        timestamp = datetime.strptime(row[0], '%d.%m.%Y %H:%M')
        load = float(row[1])/1000 # unit W to kW
        timestamps.append(timestamp)
        load_data.append(load) # unit - kW

# Sample data
data = {
    'timestamp': timestamps,
    'value': load_data
}

# Create a DataFrame
df = pd.DataFrame(data)

# Convert the 'timestamp' column to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])

february_data = df[(df['timestamp'].dt.month == 2)]

print(february_data['value'].values.tolist())
print(type(february_data['value']))