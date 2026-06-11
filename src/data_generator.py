import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


WELL_NAMES = [f"A-{i:02d}" for i in range(1, 21)]
START_DATE = datetime(2018, 1, 1)
END_DATE = datetime(2023, 12, 1)

def generate_well_metadata():
    fields = ['Field1', 'Field2', 'Field3']
    reservoirs = ['ResA', 'ResB', 'ResC']
    well_types = ['Normal Producer', 'Strong Producer', 'Water Breakthrough', 'Water Coning']
    data = []
    for well in WELL_NAMES:
        start_offset = np.random.randint(0, 12)
        start_date = START_DATE + timedelta(days=30*start_offset)
        data.append({
            'Well': well,
            'Field': np.random.choice(fields),
            'Reservoir': np.random.choice(reservoirs),
            'Well_Type': np.random.choice(well_types),
            'Start_Date': start_date.strftime('%Y-%m-%d')
        })
    df_wells = pd.DataFrame(data)
    df_wells.to_csv('data/wells.csv', index=False)

def generate_production_data():
    date_range = pd.date_range(START_DATE, END_DATE, freq='MS')
    records = []

    for well in WELL_NAMES:
        # Get well type
        well_type = get_well_type(well)
        start_date = get_start_date(well)
        for date in date_range:
            if date >= start_date:
                # Generate data based on well type
                if well_type == 'Normal Producer':
                    oil = max(0, np.random.normal(50, 5) - (date - start_date).days/365 * 2)
                    water = max(0, np.random.normal(10, 2) + (date - start_date).days/365 * 1)
                    gas = max(0, np.random.normal(20, 2) - (date - start_date).days/365 * 0.5)
                elif well_type == 'Strong Producer':
                    oil = max(0, np.random.normal(80, 3))
                    water = max(0, np.random.normal(8, 1))
                    gas = max(0, np.random.normal(25, 1))
                elif well_type == 'Water Breakthrough':
                    oil = max(0, np.random.normal(40, 5) - (date - start_date).days/365 * 3)
                    water = max(0, np.random.normal(20, 3) + (date - start_date).days/365 * 2)
                    gas = max(0, np.random.normal(18, 2))
                elif well_type == 'Water Coning':
                    # Initial stable, then increasing water
                    months_since_start = (date - start_date).days / 30
                    if months_since_start < 12:
                        oil = max(0, np.random.normal(50, 5))
                        water = max(0, np.random.normal(10, 2))
                    elif months_since_start < 24:
                        oil = max(0, np.random.normal(40, 5))
                        water = max(0, np.random.normal(20, 3))
                    else:
                        oil = max(0, np.random.normal(30, 5))
                        water = max(0, np.random.normal(30, 3))
                    gas = max(0, np.random.normal(20, 2))
                else:
                    oil, water, gas = 0, 0, 0

                records.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Well': well,
                    'Oil_Rate': max(oil, 0),
                    'Water_Rate': max(water, 0),
                    'Gas_Rate': max(gas, 0)
                })

    df = pd.DataFrame(records)
    df.to_csv('data/production.csv', index=False)

def get_well_type(well):
    df = pd.read_csv('data/wells.csv')
    return df.loc[df['Well'] == well, 'Well_Type'].values[0]

def get_start_date(well):
    df = pd.read_csv('data/wells.csv')
    return pd.to_datetime(df.loc[df['Well'] == well, 'Start_Date'].values[0])

def generate_dataset():
    generate_well_metadata()
    generate_production_data()