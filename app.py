import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from src import data_generator, calculations, diagnostics, notes

def load_data():
    if not os.path.exists('data/production.csv'):
        st.error("Data file not found. Please generate data first.")
        return pd.DataFrame()
    df = pd.read_csv('data/production.csv')
    return df

# Load data function with caching for performance
@st.cache_data
def load_data():
    df = pd.read_csv('data/production.csv', parse_dates=['Date'])
    df = calculations.calculate_metrics(df)
    return df

def main():
    st.title("Petroleum Production Performance & Surveillance Dashboard")
        # Custom styled title for the sidebar
    st.sidebar.markdown(
        """
        <h1 style='text-align: center; color: #4CAF50; font-family: Arial, sans-serif;'>
            QPD Quantum Production Dashboard
        </h1>
        """,
    unsafe_allow_html=True
)
    pages = ['Home', 'Well Analysis', 'Ranking', 'Coning Diagnostics', 'Surveillance Notes']
    choice = st.sidebar.radio('Go to', pages)

    if choice == 'Home':
        st.header("Field Production Overview")
        if st.button("Generate New Field Dataset"):
            data_generator.generate_dataset()
            st.success("Dataset generated. Please wait while it reloads...")
            st.experimental_rerun()

        df = load_data()

        total_oil = df['Oil_Rate'].sum()
        total_water = df['Water_Rate'].sum()
        avg_water_cut = df['Water_Cut'].mean()
        active_wells = df['Well'].nunique()

        # KPI cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Oil", f"{total_oil:.2f} units")
        col2.metric("Total Water", f"{total_water:.2f} units")
        col3.metric("Avg Water Cut", f"{avg_water_cut:.2%}")
        col4.metric("Active Wells", active_wells)

        # Interactive Charts
        with st.spinner("Loading production trend charts..."):
            daily_oil = df.groupby('Date')['Oil_Rate'].sum().reset_index()
            fig_oil = px.line(daily_oil, x='Date', y='Oil_Rate', title='Field Oil Production Trend')
            st.plotly_chart(fig_oil, use_container_width=True)

            daily_water = df.groupby('Date')['Water_Rate'].sum().reset_index()
            fig_water = px.line(daily_water, x='Date', y='Water_Rate', title='Field Water Production Trend')
            st.plotly_chart(fig_water, use_container_width=True)

            avg_water_cut_time = df.groupby('Date')['Water_Cut'].mean().reset_index()
            fig_wc = px.line(avg_water_cut_time, x='Date', y='Water_Cut', title='Average Water Cut Trend')
            st.plotly_chart(fig_wc, use_container_width=True)

        # Dynamic summary
        last_day = df['Date'].max()
        last_data = df[df['Date'] == last_day]
        total_oil_last = last_data['Oil_Rate'].sum()
        total_water_last = last_data['Water_Rate'].sum()
        water_cut_last = last_data['Water_Cut'].mean()

        st.markdown(f"""
        **Latest Data Summary (as of {last_day.date()}):**
        - Total Oil: {total_oil_last:.2f} units
        - Total Water: {total_water_last:.2f} units
        - Average Water Cut: {water_cut_last:.2%}
        """)

    elif choice == 'Well Analysis':
        df = load_data()
        wells = df['Well'].unique()
        selected_well = st.selectbox("Select Well", wells)
        df_well = df[df['Well'] == selected_well]

        st.subheader(f"Analysis for {selected_well}")

        col1, col2 = st.columns(2)
        with col1:
            fig_oil = px.line(df_well, x='Date', y='Oil_Rate', title='Oil Rate Trend')
            st.plotly_chart(fig_oil, use_container_width=True)
        with col2:
            fig_water = px.line(df_well, x='Date', y='Water_Rate', title='Water Rate Trend')
            st.plotly_chart(fig_water, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig_gas = px.line(df_well, x='Date', y='Gas_Rate', title='Gas Rate Trend')
            st.plotly_chart(fig_gas, use_container_width=True)
        with col4:
            fig_wc = px.line(df_well, x='Date', y='Water_Cut', title='Water Cut Trend')
            st.plotly_chart(fig_wc, use_container_width=True)

        # Get the latest row from the DataFrame
        latest = df_well.iloc[-1]

        # Check if 'Well_Type' exists in the latest row
        well_type = latest['Well_Type'] if 'Well_Type' in latest else 'Data not available'

        # Construct the summary string with proper formatting
        summary = (
            f"**Current Metrics:**\n"
            f"- Oil Rate: {latest['Oil_Rate']:.2f}\n"
            f"- Water Cut: {latest['Water_Cut']:.2%}\n"
            f"- GOR: {latest['GOR']:.2f}\n"
            f"- WOR: {latest['WOR']:.2f}\n"
            f"- Well Type: {well_type}"
        )

        # Display the summary in Streamlit
        st.markdown(summary)
        # Interpretation based on latest data
        interpretation = "Stable Performance"
        if latest['Water_Cut'] > 0.5:
            interpretation = "Increasing Water Production"
        if latest['Oil_Rate'] < 20:
            interpretation = "Declining Producer"
        st.info(f"**Engineering Interpretation:** {interpretation}")

    elif choice == 'Ranking':
        df = load_data()
        latest_df = df.groupby('Well').last().reset_index()

        st.subheader("Top Oil Producers")
        top_oil = latest_df[['Well', 'Oil_Rate']].sort_values('Oil_Rate', ascending=False)
        st.dataframe(top_oil.style.background_gradient(cmap='Greens'))

        st.subheader("Wells with Highest Water Cut")
        high_wc = latest_df[['Well', 'Water_Cut']].sort_values('Water_Cut', ascending=False)
        st.dataframe(high_wc.style.background_gradient(cmap='Blues'))

        st.subheader("Wells with Highest WOR")
        high_wor = latest_df[['Well', 'WOR']].sort_values('WOR', ascending=False)
        st.dataframe(high_wor.style.background_gradient(cmap='Reds'))

    elif choice == 'Coning Diagnostics':
        df = load_data()
        risks_df = diagnostics.detect_coning_risk(df)
        st.subheader("Water Coning Risk Assessment")
        for _, row in risks_df.iterrows():
            color = 'green' if row['Coning_Risk'] == 'Low' else ('orange' if row['Coning_Risk'] == 'Medium' else 'red')
            st.markdown(f"""
            **Well {row['Well']}**  
            Risk Level: <span style="color:{color}; font-weight: bold;">{row['Coning_Risk']}</span>  
            Reason: Water cut {row['Water_Cut']:.2%}, Oil decline {row['Oil_Decline']:.2f}%
            """, unsafe_allow_html=True)

        st.dataframe(risks_df)

    elif choice == 'Surveillance Notes':
        df = load_data()
        summary_text = notes.generate_summary(df)
        st.text_area("Production Surveillance Summary", value=summary_text, height=200)

if __name__ == '__main__':
    main()