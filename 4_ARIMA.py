import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.stattools import adfuller

# Load the prepared data
data = pd.read_csv('analyse_electric_load_data.csv', parse_dates=['timestamp'], index_col='timestamp')

# Explicitly set the frequency to hourly ('H')
data = data.asfreq('H')

# Check if the time series is stationary
result = adfuller(data['load'])
print(f'ADF Statistic: {result[0]}')
print(f'p-value: {result[1]}')

# If the time series is not stationary, you may need to difference it to make it stationary.
# Example:
# data['load_diff'] = data['load'].diff().dropna()

# Split the data into training and testing sets
train_size = int(len(data) * 0.8)
train, test = data[:train_size], data[train_size:]

# Define and fit an ARIMA model
p, d, q = 2, 0, 2  # Example ARIMA hyperparameters (2,0,1)
model = ARIMA(train['load'], exog=train[['day_of_week', 'month', 'load_lag1', 'load_lag2']], order=(p, d, q))
# model = ARIMA(train['load'], exog=train[['day_of_week', 'month']], order=(p, d, q))
model_fit = model.fit()
print(model_fit.summary())

# Make predictions on the test set
predictions = model_fit.forecast(steps=len(test), exog=test[['day_of_week', 'month', 'load_lag1', 'load_lag2']])
# predictions = model_fit.forecast(steps=len(test), exog=test[['day_of_week', 'month']])

# Calculate and print the RMSE
rmse = mean_squared_error(test['load'], predictions, squared=False)
print(f'ARIMA RMSE: {rmse}')

# Visualize the actual vs. predicted values
plt.figure(figsize=(12, 6))
plt.plot(test.index, test['load'], label='Actual Load')
plt.plot(test.index, predictions, label='Predicted Load', color='orange')
plt.xlabel('Timestamp')
plt.ylabel('Load')
plt.title('ARIMA Forecasting')
plt.legend()
plt.grid(True)
plt.show()

# Save the ARIMA model to a file
model_fit.save('arima_model.pkl')