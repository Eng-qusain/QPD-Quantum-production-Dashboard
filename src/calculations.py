import pandas as pd

def calculate_metrics(df):
    df = df.copy()
    df['Water_Cut'] = df['Water_Rate'] / (df['Oil_Rate'] + df['Water_Rate'])
    df['GOR'] = df['Gas_Rate'] / df['Oil_Rate']
    df['WOR'] = df['Water_Rate'] / df['Oil_Rate']
    df = df.sort_values(['Well', 'Date'])

    # Calculate decline
    df['Oil_Rate_Prev'] = df.groupby('Well')['Oil_Rate'].shift(1)
    df['Oil_Decline_Percent'] = (df['Oil_Rate_Prev'] - df['Oil_Rate']) / df['Oil_Rate_Prev'] * 100
    df['Oil_Decline_Percent'] = df['Oil_Decline_Percent'].fillna(0)

    return df