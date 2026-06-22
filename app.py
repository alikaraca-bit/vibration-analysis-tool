import streamlit as st
import pandas as pd

# 1. SETUP UPLOADERS
st.sidebar.header("Upload Files")
coord_file = st.sidebar.file_uploader("Upload Coordinates CSV", type=['csv'])
freq_file = st.sidebar.file_uploader("Upload Frequencies CSV", type=['csv'])

# 2. ONLY RUN ANALYSIS IF FILES ARE UPLOADED
if coord_file is not None and freq_file is not None:
    # Load and process data
    df_coord = pd.read_csv(coord_file)
    df_freq = pd.read_csv(freq_file)
    
    # ... [Your merging/processing code here] ...
    
    # Now that df_valid is created, we can safely show the selectbox
    df_valid['timestamp'] = pd.to_datetime(df_valid['timestamp'])
    time_options = df_valid['timestamp'].dt.strftime('%H:%M:%S').unique()
    
    selected_time = st.selectbox("Select Timestamp", time_options)
    
    # ... [Your plotting code here] ...

else:
    # This shows a friendly message instead of an error
    st.info("Please upload both CSV files in the sidebar to begin analysis.")
