import streamlit as st
import pandas as pd

# ... your imports and functions ...

# 1. SIDEBAR UPLOADERS
coord_file = st.sidebar.file_uploader("Upload Coordinates CSV", type=['csv'])
freq_file = st.sidebar.file_uploader("Upload Frequencies CSV", type=['csv'])

# 2. WRAP EVERYTHING IN THE DATA CHECK
if coord_file and freq_file:
    # Perform your data loading and processing here
    df_coord = pd.read_csv(coord_file)
    df_freq = pd.read_csv(freq_file)
    
    # Define df_valid HERE inside the block
    df_valid = ... # Your merging logic here
    
    # NOW the selectbox will work because df_valid exists
    selected_time = st.selectbox("Select Timestamp", df_valid['timestamp'].dt.strftime('%H:%M:%S').unique())
    
    # ... rest of your plot code ...
else:
    st.info("Please upload both CSV files to see the analysis.")
