def generate_summary(df):
    total_oil = df['Oil_Rate'].sum()
    total_water = df['Water_Rate'].sum()
    avg_water_cut = df['Water_Cut'].mean()
    summary = (
        f"Total Oil: {total_oil:.2f}\n"
        f"Total Water: {total_water:.2f}\n"
        f"Average Water Cut: {avg_water_cut:.2%}\n"
    )
    return summary
