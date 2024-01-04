import csv
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

timestamp_interval = 15/60 # minute

# Load data from a CSV file
timestamps = []
load_data = [] # one year

with open('load_data_cleaned.csv', 'r') as csvfile:#load_data_cleaned.csv
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row if present
    for row in reader:
        # Assuming the first column is timestamp in 'dd.mm.yyyy HH:MM' format
        timestamp = datetime.strptime(row[0], '%d.%m.%Y %H:%M')
        load = float(row[1])/1 # (data in kW) not need to change unit W to kW 
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

filtered_data = []
# Iterate through each month
for month in range(1, 13):
    # Filter data for the current month
    filtered_month_data = df[(df['timestamp'].dt.month == month)]
    filtered_data.append(filtered_month_data)

# print(filtered_data)


def shaving(charge_power_percentage,discharge_power_percentage,timestamps, load_data):
    # Calculate the maximum and minimum load values
    max_load_value = max(load_data)
    min_load_value = min(load_data)
    # Define the charge power and discharge power as percentages of the maximum and minimum load
    # charge_power_percentage = 30  # You can adjust this percentage as needed
    # discharge_power_percentage = 85  # You can adjust this percentage as needed

    

    # Battery parameters
    max_battery_capacity_kWh = 100  # Replace with your battery capacity in kWh


    # Initialize variables
    available_battery_capacity_kWh = max_battery_capacity_kWh/2  # Battery energy level in kWh
    space_battery_capacity_kWh = max(max_battery_capacity_kWh - available_battery_capacity_kWh,0)
    peak_shaved_load = []
    charge_lvl = []
    discharge_lvl = []
    battery_soc = []  # To store SOC values
    soc_percentage = (available_battery_capacity_kWh/max_battery_capacity_kWh)* 100
    max_load_predict = 0

    # Perform peak shaving
    for timestamp, load in zip(timestamps, load_data):
        max_load_predict = max(max_load_predict,load)

        # Calculate max_charge_power_kW and max_discharge_power_kW as percentages of load values
        # charge_lvl_power_kW = max(max_load_predict * (charge_power_percentage / 100),500)
        # discharge_lvl_power_kW = max(max_load_predict * (discharge_power_percentage / 100),500)
        charge_lvl_power_kW = 1900
        discharge_lvl_power_kW = 1900
        charge_lvl.append([charge_lvl_power_kW])
        discharge_lvl.append([discharge_lvl_power_kW])
        
        # Calculate the excess load (load - discharge)
        excess_load_power = max(load - discharge_lvl_power_kW,0)# battery discharge
        lack_load_power = max(charge_lvl_power_kW - load,0)# battery charge
        
        # Calculate the available space in the battery for charging (up to 100% SOC)
        
        battery_supply_power = 0
        battery_supply_energy = 0
        battery_consume_power = 0
        battery_consume_energy = 0
        
        # battery discharge
        if excess_load_power > 0:
            excess_load_energy = excess_load_power * timestamp_interval
            
            if available_battery_capacity_kWh > 0:
                if excess_load_energy > available_battery_capacity_kWh:
                    battery_supply_energy = available_battery_capacity_kWh
                    battery_supply_power = battery_supply_energy/timestamp_interval
                else:
                    battery_supply_energy = excess_load_energy
                    battery_supply_power = battery_supply_energy/timestamp_interval
            else:
                battery_supply_power = 0
                battery_supply_energy = 0 # Battery empty charged
        else:
            battery_supply_power = 0
            battery_supply_energy = 0
            
        # battery charge
        if lack_load_power > 0:
            lack_load_energy = lack_load_power * timestamp_interval
            if space_battery_capacity_kWh > 0:
                if lack_load_energy > space_battery_capacity_kWh: 
                    battery_consume_energy = space_battery_capacity_kWh
                    battery_consume_power = battery_consume_energy/timestamp_interval
                else:
                    battery_consume_energy = lack_load_energy
                    battery_consume_power = battery_consume_energy/timestamp_interval
            else:
                battery_consume_power = 0
                battery_consume_energy = 0 # Battery fully charged
        else:
            battery_consume_power = 0
            battery_consume_energy = 0   
            
        available_battery_capacity_kWh = available_battery_capacity_kWh + battery_consume_energy - battery_supply_energy
        space_battery_capacity_kWh = max(max_battery_capacity_kWh - available_battery_capacity_kWh,0)
        # Calculate SOC (State of Charge) as a percentage of battery capacity
        soc_percentage = (available_battery_capacity_kWh/max_battery_capacity_kWh)* 100
        battery_soc.append([timestamp, soc_percentage])
        peak_shaved_load.append([timestamp, load - battery_supply_power + battery_consume_power])
        

    # Calculate the peak shaved load
    peak_shaved_load = np.array(peak_shaved_load)
    peak_shaved_load_max = max(peak_shaved_load[:, 1])

    # Calculate the peak load reduction
    peak_load_reduction = max(load_data) - max(peak_shaved_load[:, 1])

    if peak_load_reduction > 100:
        print(f"charge,discharge: {charge_power_percentage},{discharge_power_percentage} kW")
        print(f"Peak load reduction: {peak_load_reduction} kW")


    # Extract timestamps and load values for plotting
    timestamps = [row[0] for row in peak_shaved_load]
    shaved_load_values = [row[1] for row in peak_shaved_load]

    # Extract timestamps and SOC values for plotting SOC
    soc_timestamps = [row[0] for row in battery_soc]
    soc_values = [row[1] for row in battery_soc]

    # Plot load data, peak shaved load, battery energy level, and SOC
    plt.figure(figsize=(12, 8))

    # Plot Load Data
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, load_data, label='Original Load', linestyle='--', color='blue')
    plt.plot(timestamps, shaved_load_values, label='Peak Shaved Load', color='green')
    plt.axhline(y=peak_shaved_load_max, color='darkgreen', linestyle=':', label=f'peak_shaved_load_max')
    plt.plot(timestamps, discharge_lvl, color='orange', linestyle=':', label=f'{discharge_power_percentage}% Discharge Power')
    plt.plot(timestamps, charge_lvl, color='red', linestyle=':', label=f'{charge_power_percentage}% Charge Power')
    #plt.plot(timestamps, [available_battery_capacity_kWh] * len(timestamps), linestyle=':', color='purple', label='Battery Capacity')
    plt.xlabel('Timestamp')
    plt.ylabel('Load (kW)')
    plt.title('Peak Shaving and Battery Operation')
    plt.legend()
    plt.grid(True)

    # Plot SOC
    plt.subplot(2, 1, 2)
    plt.plot(soc_timestamps, soc_values, label='SOC', color='blue')
    plt.xlabel('Timestamp')
    plt.ylabel('SOC (%)')
    plt.title('Battery State of Charge (SOC)')
    plt.ylim([-10, 110])  # Limit the y-axis to the range of 0% to 100%
    plt.grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Peak load reduction: {peak_load_reduction} kW")
    
    return peak_load_reduction


# max_buff = []
# for i in range(30, 40,5):
#     for j in range(80, 90,5):
#         max_val = shaving(i,j,timestamps, load_data)
#         max_buff.append(max_val)

        
# print(f"max: {max(max_buff)}")
for i in range(0,12):
    load_data_monthly = filtered_data[i]['value'].values.tolist()
    max_val = shaving(89,90,timestamps, load_data_monthly)
    print(f"max: {max_val}")
