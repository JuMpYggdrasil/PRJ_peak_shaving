import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMAResults


# Load the prepared data and specify the last timestamp
data = pd.read_csv('analyse_electric_load_data.csv', parse_dates=['timestamp'], index_col='timestamp')
last_timestamp = data.index[-1]
load_lag1 = data['load'].iat[-1]
load_lag2 = data['load_lag1'].iat[-1]

# Specify the number of steps to forecast 
forecast_steps = 1 # forcast next hour

# Generate timestamps for the forecasted values
forecast_timestamps = [last_timestamp + timedelta(hours=i) for i in range(1, forecast_steps + 1)]

# Create exogenous data for the same future timestamps
# Replace this with your actual exogenous data generation
exog_data = pd.DataFrame(index=forecast_timestamps)
exog_data['day_of_week'] = [timestamp.dayofweek for timestamp in forecast_timestamps]
exog_data['month'] = [timestamp.month for timestamp in forecast_timestamps]
exog_data['load_lag1'] = load_lag1  # Replace with actual values if available
exog_data['load_lag2'] = load_lag2  # Replace with actual values if available

# Load the ARIMA model from the saved file
loaded_model = ARIMAResults.load('arima_model.pkl')

# Now, you have exogenous data aligned with the forecast timestamps
print(exog_data)

# Forecast using the loaded model
forecast_values = loaded_model.forecast(steps=forecast_steps, exog=exog_data)

# Print the forecasted values
print(f'Forecasted Values: {forecast_values}')
