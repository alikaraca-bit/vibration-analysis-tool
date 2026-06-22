import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Set page to wide layout
st.set_page_config(layout="wide")
st.title("Vibration Analysis Dashboard")

# 1. SIDEBAR UPLOADERS
st.sidebar.header("Upload Files")
coord_file = st.sidebar.file_uploader("Upload Coordinates CSV", type=['csv'])
freq_file = st.sidebar.file_uploader("Upload Frequencies CSV", type=['csv'])

# 2. ONLY RUN ANALYSIS IF FILES ARE UPLOADED
if coord_file is not None and freq_file is not None:
    # Load and process data
    df_coord = pd.read_csv(coord_file)
    df_freq = pd.read_csv(freq_file)
    
    # Convert timestamps
    df_coord['timestamp'] = pd.to_datetime(df_coord['timestamp'])
    df_freq['timestamp'] = pd.to_datetime(df_freq['timestamp'])
    
    # Sort and Merge
    df_coord = df_coord.sort_values('timestamp')
    df_freq = df_freq.sort_values('timestamp')
    
    df_merged = pd.merge_asof(df_coord, df_freq, on='timestamp', direction='nearest', tolerance=pd.Timedelta('0.5s'))
    df_valid = df_merged.dropna(subset=['IC3_SAP_MON_MASTER_SIGNAL_SP_1_SeverityRange_2_Severity']).copy()
    
    # 3. 3D CUTTING PATH PLOT
    st.subheader("3D Cutting Path")
    fig = go.Figure()
    
    fig.add_trace(go.Scatter3d(
        x=df_merged['RA1_1_Pos_BCS'], y=df_merged['RA2_1_Pos_BCS'], z=df_merged['RA3_1_Pos_BCS'],
        mode='lines', line=dict(color='lightgrey', width=3), name='Machine Path'
    ))
    
    fig.add_trace(go.Scatter3d(
        x=df_valid['RA1_1_Pos_BCS'], y=df_valid['RA2_1_Pos_BCS'], z=df_valid['RA3_1_Pos_BCS'],
        mode='markers',
        marker=dict(size=4, color=df_valid['IC3_SAP_MON_MASTER_SIGNAL_SP_1_SeverityRange_2_Severity'], 
                    colorscale='Jet', opacity=1),
        name='Severity Logs'
    ))
    
    fig.update_layout(scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'), margin=dict(l=0, r=0, b=0, t=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. FFT SPECTRUM VIEWER
    st.subheader("FFT Spectrum Viewer")
    time_options = df_valid['timestamp'].dt.strftime('%H:%M:%S').unique()
    selected_time = st.selectbox("Select Timestamp", time_options)
    
    # FFT Plotting Logic
    row = df_valid[df_valid['timestamp'].dt.strftime('%H:%M:%S') == selected_time].iloc[0]
    freq_cols = [f'IC3_SAP_MON_MASTER_SIGNAL_SP_1_Peak_{i}_Frequency' for i in range(1, 10)]
    amp_cols = [f'IC3_SAP_MON_MASTER_SIGNAL_SP_1_Peak_{i}_Amplitude' for i in range(1, 10)]
    
    freqs = row[freq_cols].values.astype(float)
    amps = row[amp_cols].values.astype(float)
    
    fig_fft, ax = plt.subplots(figsize=(10, 4))
    ax.stem(freqs, amps, basefmt=" ")
    ax.set_title(f"FFT at {selected_time}")
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig_fft)

else:
    st.info("Please upload both CSV files in the sidebar to begin analysis.")
