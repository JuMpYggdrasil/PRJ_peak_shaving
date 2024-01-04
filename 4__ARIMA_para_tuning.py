import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error

# Load the prepared data
data = pd.read_csv('analyse_electric_load_data.csv', parse_dates=['timestamp'], index_col='timestamp')
data = data.asfreq('H')

# Split the data into training and testing sets
train_size = int(len(data) * 0.8)
train, test = data[:train_size], data[train_size:]

# Define a range of hyperparameters to search
p_values = range(0, 2)  # Example range for p
d_values = range(0, 2)  # Example range for d
q_values = range(0, 3)  # Example range for q

best_rmse = float('inf')
best_params = (0, 0, 0)

for p in p_values:
    for d in d_values:
        for q in q_values:
            try:
                model = ARIMA(train['load'], order=(p, d, q))
                model_fit = model.fit()
                predictions = model_fit.forecast(steps=len(test))
                rmse = np.sqrt(mean_squared_error(test['load'], predictions))
                if rmse < best_rmse:
                    best_rmse = rmse
                    best_params = (p, d, q)
                    print(f'ARIMA({p},{d},{q}) RMSE: {rmse}')
            except Exception as e:
                continue

print(f'Best ARIMA({best_params[0]},{best_params[1]},{best_params[2]}) RMSE: {best_rmse}')
