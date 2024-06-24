import pandas as pd

# Load the historical data with the specified timestamp format
# date_format = '%d.%m.%Y %H:%M'
# data = pd.read_csv('BCF_2022_homer.csv', parse_dates=['Date'], date_format=date_format)
date_format = '%d/%m/%Y %H.%M'
data = pd.read_csv('combined_data_robinson_edit.csv', parse_dates=['Date'], date_format=date_format)
# data = pd.read_csv('load_data_cleaned.csv', parse_dates=['Date'], date_format=date_format)
data.rename(columns={'Date': 'timestamp','Load': 'load'}, inplace=True)

# Ensure the timestamp column is set as the index
data.set_index('timestamp', inplace=True)

# Check for missing values and handle them if necessary
if data.isnull().any().any():
    data = data.interpolate()  # Interpolate missing values
    # or
    # data = data.fillna(method='ffill')  # Forward fill missing values
    # data = data.fillna(method='bfill')  # Backward fill missing values
    



# Aggregate data to hourly intervals
hourly_data = data.resample('H').mean()  # You can use 'D' for daily aggregation

# Optionally, add additional features like day of the week
hourly_data['day_of_week'] = hourly_data.index.dayofweek

# Add a 'month' column
hourly_data['month'] = hourly_data.index.month

# Save the prepared data to a CSV file
hourly_data.to_csv('prepared_electric_load_data.csv')


# Aggregate data to hourly intervals
daily_peak_data = data.resample('D').max()  # You can use 'D' for daily aggregation

# Optionally, add additional features like day of the week
daily_peak_data['day_of_week'] = daily_peak_data.index.dayofweek

# Add a 'month' column
daily_peak_data['month'] = daily_peak_data.index.month

# Save the prepared data to a CSV file
daily_peak_data.to_csv('daily_peak_load_data.csv')


