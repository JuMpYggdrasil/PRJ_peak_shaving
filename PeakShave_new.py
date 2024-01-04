import numpy as np
from datetime import datetime, timedelta, time
import matplotlib.pyplot as plt
import pandas as pd

timestamp_interval = 15/60  # minute

# Load data from a CSV file
timestamps = []
load_data = []  # one year

# Load data using pandas
date_format = '%d.%m.%Y %H:%M'
df = pd.read_csv('BCF_2022_homer.csv', parse_dates=['Date'], date_format=date_format)
# data = pd.read_csv('load_data_cleaned.csv', parse_dates=['Date'], date_format=date_format)
df.rename(columns={'Date': 'timestamp','Load': 'load'}, inplace=True)

# Ensure the timestamp column is set as the index
df.set_index('timestamp', inplace=True)

# Extract timestamps and load data from the DataFrame
timestamps = df.index  # Assuming the index contains timestamp values
load_data = df['load']  # Assuming 'load' is the column with load data


filtered_data = []

# Iterate through each month
for month in range(1, 13):
    # Filter data for the current month
    filtered_month_data = df[df.index.month == month]
    filtered_data.append(filtered_month_data)

# Define the shaving function
def shaving(charge_power_percentage,discharge_power_percentage,timestamps, load_data):
    # Calculate the maximum and minimum load values
    max_load_value = max(load_data)
    min_load_value = min(load_data)
    # Define the charge power and discharge power as percentages of the maximum and minimum load
    # charge_power_percentage = 30  # You can adjust this percentage as needed
    # discharge_power_percentage = 85  # You can adjust this percentage as needed

    

    # Battery parameters
    ## Battery tesla 1 uint: 700,000 THB energy 135 kW-hr, power 5.5 kW 
    ## GRID scaled battery: 000,000 THB energy 1000 kW-hr, power 350 kW 
    max_battery_capacity_kWh = 100  # Replace with your battery capacity in kWh
    battery_power_limit = 40 # kW


    # Initialize variables
    available_battery_capacity_kWh = max_battery_capacity_kWh  # Battery energy level in kWh
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
        
        # # FIX
        # discharge_lvl_power_kW = 2000
        # charge_lvl_power_kW = 1000
        # # dis-charge when load > discharge_lvl_power_kW
        # # charge when load < charge lvl
            
        # discharge_lvl_power_kW > charge_lvl_power_kW
        is_weekday = timestamp.weekday() < 5
        time_of_day = timestamp.time()
        is_within_on_peak_time_range = time_of_day > time(9, 0) and time_of_day <= time(22, 0) # on-peak time
        is_within_custom_time_range = time_of_day > time(17, 0) and time_of_day <= time(22, 0) # dis-charge time

        if is_weekday and is_within_on_peak_time_range:# on peak (want to discharge -- low discharge lvl)
            if is_within_custom_time_range:
                discharge_lvl_power_kW = 0
                charge_lvl_power_kW = 0
            else: # do nothing
                discharge_lvl_power_kW = 3000
                charge_lvl_power_kW = 0
                
        else:# off peak (want to charge -- high charge lvl)
            discharge_lvl_power_kW = 3000
            charge_lvl_power_kW = 3000
            
        
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
                    if battery_supply_power>battery_power_limit:
                        battery_supply_power = battery_power_limit
                        battery_supply_energy = battery_power_limit*timestamp_interval
                else:
                    battery_supply_energy = excess_load_energy
                    battery_supply_power = battery_supply_energy/timestamp_interval
                    if battery_supply_power>battery_power_limit:
                        battery_supply_power = battery_power_limit
                        battery_supply_energy = battery_power_limit*timestamp_interval
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
                    if battery_consume_power>battery_power_limit:
                        battery_consume_power = battery_power_limit
                        battery_consume_energy = battery_power_limit*timestamp_interval
                else:
                    battery_consume_energy = lack_load_energy
                    battery_consume_power = battery_consume_energy/timestamp_interval
                    if battery_consume_power>battery_power_limit:
                        battery_consume_power = battery_power_limit
                        battery_consume_energy = battery_power_limit*timestamp_interval
            else:
                battery_consume_power = 0
                battery_consume_energy = 0 # Battery fully charged
        else:
            battery_consume_power = 0
            battery_consume_energy = 0   
            
        available_battery_capacity_kWh = max(available_battery_capacity_kWh + battery_consume_energy - battery_supply_energy,0)
        space_battery_capacity_kWh = max(max_battery_capacity_kWh - available_battery_capacity_kWh,0)
        # Calculate SOC (State of Charge) as a percentage of battery capacity
        soc_percentage = max((available_battery_capacity_kWh/max_battery_capacity_kWh)* 100,0)
        battery_soc.append([timestamp, soc_percentage])
        peak_shaved_load.append([timestamp, load - battery_supply_power + battery_consume_power])
        

    # Calculate the peak shaved load
    peak_shaved_load = np.array(peak_shaved_load)
    peak_shaved_load_max = max(peak_shaved_load[10:, 1])

    # Calculate the peak load reduction
    peak_load_reduction = max(load_data) - peak_shaved_load_max

    # if peak_load_reduction > 10:
    #     # print(f"charge,discharge: {charge_power_percentage},{discharge_power_percentage} kW")
    #     print(f"Peak load reduction: {peak_load_reduction} kW")


    # Extract timestamps and load values for plotting
    timestamps = [row[0] for row in peak_shaved_load]
    shaved_load_values = [row[1] for row in peak_shaved_load]

    # Extract timestamps and SOC values for plotting SOC
    soc_timestamps = [row[0] for row in battery_soc]
    soc_values = [row[1] for row in battery_soc]
    
    # Create a figure and a set of subplots with specified figure size
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(12, 8))  # figsize sets the size of the figure

    # Plot Load Data on the first subplot
    ax1.plot(timestamps, load_data, label='Original Load', linestyle='--', color='blue')
    ax1.plot(timestamps, shaved_load_values, label='Peak Shaved Load', color='green')
    ax1.axhline(y=peak_shaved_load_max, color='darkgreen', linestyle=':', label=f'peak_shaved_load_max')
    ax1.plot(timestamps, discharge_lvl, color='orange', linestyle=':', label=f'{discharge_power_percentage}% Discharge Power')
    ax1.plot(timestamps, charge_lvl, color='red', linestyle=':', label=f'{charge_power_percentage}% Charge Power')
    ax1.set_xlabel('Timestamp')
    ax1.set_ylabel('Load (kW)')
    ax1.set_title('Peak Shaving and Battery Operation')
    ax1.legend()
    ax1.grid(True)

    # Plot SOC on the second subplot
    ax2.plot(soc_timestamps, soc_values, label='SOC', color='blue')
    ax2.set_xlabel('Timestamp')
    ax2.set_ylabel('SOC (%)')
    ax2.set_title('Battery State of Charge (SOC)')
    ax2.set_ylim([-10, 110])  # Limit the y-axis to the range of 0% to 100%
    ax2.grid(True)

    # Adjust layout
    plt.tight_layout()
    plt.show()

    print(f"Peak load reduction: {peak_load_reduction} kW")
    
    return peak_load_reduction

# Loop through the filtered data for each month
for i in range(0, 12):
    load_data_monthly = filtered_data[i]['load'].values.tolist()
    max_val = shaving(89, 90, timestamps, load_data_monthly)
    print(f"max: {max_val}")
