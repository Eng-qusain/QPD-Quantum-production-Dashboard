import pandas as pd

def detect_coning_risk(df):
    risks = []
    for well in df['Well'].unique():
        df_well = df[df['Well'] == well]
        latest = df_well.iloc[-1]
        water_cut = latest['Water_Cut']
        oil_decline = latest['Oil_Decline_Percent']
        risk_level = 'Low'

        if water_cut > 0.7 and oil_decline > 20:
            risk_level = 'High'
        elif water_cut > 0.5 and oil_decline > 10:
            risk_level = 'Medium'
        elif water_cut < 0.4:
            risk_level = 'Low'

        risks.append({
            'Well': well,
            'Water_Cut': water_cut,
            'Oil_Decline': oil_decline,
            'Coning_Risk': risk_level
        })

    return pd.DataFrame(risks)