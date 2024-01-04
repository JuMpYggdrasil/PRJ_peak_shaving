import pandas as pd
import matplotlib.pyplot as plt

# Load your electrical load data into a Pandas DataFrame
df = pd.read_csv('analyse_electric_load_data.csv', parse_dates=['timestamp'])
# df.rename(columns={'Date': 'timestamp','Load': 'load'}, inplace=True)

# Assuming your DataFrame has a 'timestamp' column, you can set it as the index
df.set_index('timestamp', inplace=True)

# Extract data for weekdays (Monday to Friday)
weekdays = df[(df.index.dayofweek >= 0) & (df.index.dayofweek < 5)]

# Extract data for weekends (Saturday and Sunday)
weekends = df[(df.index.dayofweek >= 5)]

# Calculate hourly averages for each hour of the day for all 7 days of the week
day_patterns = [[] for _ in range(7)]
for day in range(7):
    day_data = df[df.index.dayofweek == day]
    for hour in range(24):
        day_patterns[day].append(day_data['load'][day_data.index.hour == hour].mean())
        
# Create a list of day labels for the legend
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# Calculate hourly averages for each hour of the day
weekdays_pattern = []
weekends_pattern = []
for hour in range(24):
    weekdays_pattern.append(weekdays['load'][weekdays.index.hour == hour].mean())
    weekends_pattern.append(weekends['load'][weekends.index.hour == hour].mean())
    


# Create a list of hours (0 to 23) for the x-axis
hours = list(range(24))

# Plot the hourly data for weekdays and weekends
plt.figure(figsize=(12, 6))
plt.plot(hours, weekdays_pattern, label='weekdays_pattern', marker='o')
plt.plot(hours, weekends_pattern, label='weekends_pattern', marker='o')
plt.title('Hourly Electrical Load Profile')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Load (kW)')
plt.legend()
plt.grid(True)
plt.xticks(hours)
plt.show()

# Plot the hourly data for all 7 days of the week on the same page
plt.figure(figsize=(12, 6))
for day in range(7):
    plt.plot(hours, day_patterns[day], label=days[day], marker='o')

plt.title('Hourly Electrical Load Profile for All Days of the Week')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Load (kW)')
plt.legend()
plt.grid(True)
plt.xticks(hours)
plt.show()


# Reset the index if you want to keep the 'timestamp' column
weekdays.reset_index(inplace=True)
weekends.reset_index(inplace=True)

# Save the DataFrames to separate CSV files
weekdays.to_csv('weekdays_data.csv', index=False)
weekends.to_csv('weekends_data.csv', index=False)
