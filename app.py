import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# 1. PAGE SETUP
st.set_page_config(layout="wide")
st.title("Vibration Analysis Dashboard")

# 2. FILE UPLOADERS
st.sidebar.header("Upload Files")
coord_file = st.sidebar.file_uploader("Upload Coordinates CSV", type=['csv'])
freq_file = st.sidebar.file_uploader("Upload Frequencies CSV", type=['csv'])

# 3. RUN ANALYSIS IF FILES EXIST
if coord_file is not None and freq_file is not None:
    # --- DATA PROCESSING ---
    df_coord = pd.read_csv(coord_file)
    df_freq = pd.read_csv(freq_file)
    
    df_coord['timestamp'] = pd.to_datetime(df_coord['timestamp'])
    df_freq['timestamp'] = pd.to_datetime(df_freq['timestamp'])
    
    df_coord = df_coord.sort_values('timestamp')
    df_freq = df_freq.sort_values('timestamp')
    
    df_merged = pd.merge_asof(df_coord, df_freq, on='timestamp', direction='nearest', tolerance=pd.Timedelta('0.5s'))
    df_valid = df_merged.dropna(subset=['IC3_SAP_MON_MASTER_SIGNAL_SP_1_SeverityRange_2_Severity']).copy()
    
    # --- 3D INTERACTIVE PLOT ---
    st.subheader("Interactive XYZ Cutting Path")
    fig = go.Figure()
    
    # Background Grey Path
    fig.add_trace(go.Scatter3d(
        x=df_merged['RA1_1_Pos_BCS'], y=df_merged['RA2_1_Pos_BCS'], z=df_merged['RA3_1_Pos_BCS'],
        mode='lines', line=dict(color='lightgrey', width=3), name='Machine Path', hoverinfo='none'
    ))
    
    # Hover text formatting
    hover_text = [
        f"Time: {t}<br>Feed Rate: {f:.1f}<br>Severity: {s:.2f}" 
        for t, f, s in zip(
            df_valid['timestamp'].dt.strftime('%H:%M:%S.%f').str[:-3], 
            df_valid['Path_Feedrate'], 
            df_valid['IC3_SAP_MON_MASTER_SIGNAL_SP_1_SeverityRange_2_Severity']
        )
    ]
    
    # Colored Severity Dots
    fig.add_trace(go.Scatter3d(
        x=df_valid['RA1_1_Pos_BCS'], y=df_valid['RA2_1_Pos_BCS'], z=df_valid['RA3_1_Pos_BCS'],
        mode='markers',
        marker=dict(
            size=4, 
            color=df_valid['IC3_SAP_MON_MASTER_SIGNAL_SP_1_SeverityRange_2_Severity'], 
            colorscale='Jet', 
            colorbar=dict(title='Severity', thickness=15, len=0.7),
            opacity=1
        ),
        text=hover_text,
        hoverinfo='text',
        name='Severity Logs'
    ))
    
    fig.update_layout(
        scene=dict(xaxis_title='X (mm)', yaxis_title='Y (mm)', zaxis_title='Z (mm)'), 
        margin=dict(l=0, r=0, b=0, t=0),
        height=650
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # --- FFT SPECTRUM VIEWER ---
    st.subheader("FFT Spectrum Viewer")
    
    # Create the time dropdown
    df_valid['time_str'] = df_valid['timestamp'].dt.strftime('%H:%M:%S')
    time_options = df_valid['time_str'].unique()
    selected_time = st.selectbox("Select Timestamp to view its 9-Point FFT:", time_options)
    
    # Extract data for the selected time
    row = df_valid[df_valid['time_str'] == selected_time].iloc[0]
    freq_cols = [f'IC3_SAP_MON_MASTER_SIGNAL_SP_1_Peak_{i}_Frequency' for i in range(1, 10)]
    amp_cols = [f'IC3_SAP_MON_MASTER_SIGNAL_SP_1_Peak_{i}_Amplitude' for i in range(1, 10)]
    
    freqs = row[freq_cols].values.astype(float)
    amps = row[amp_cols].values.astype(float)
    
    spindle_rpm = row['SP1_Speed']
    f_spindle = spindle_rpm / 60 if pd.notnull(spindle_rpm) else 0
    
    # Create the Stem Plot
    fig_fft, ax = plt.subplots(figsize=(12, 5))
    ax.stem(freqs, amps, basefmt=" ")
    
    # Add the Red Dashed Harmonic Lines
    if f_spindle > 0 and not np.isnan(f_spindle):
        max_f = np.nanmax(freqs)
        if np.isnan(max_f) or max_f == 0: max_f = 500
        num_harmonics = int(np.ceil((max_f + 50) / f_spindle))
        
        for k in range(1, num_harmonics + 1):
            f_k = k * f_spindle
            ax.axvline(x=f_k, color='red', linestyle='--', alpha=0.3)
            ax.text(f_k, ax.get_ylim()[1]*0.95, f"{k}x", color='red', alpha=0.5, ha='center', fontsize=8)
            
    # Add text labels to the peaks (tilted 45 degrees)
    for f, a in zip(freqs, amps):
        if not np.isnan(f) and not np.isnan(a):
            ax.text(f + 1, a, f"{f:.1f} Hz", rotation=45, va='bottom', ha='left', fontsize=9)
            
    ax.set_title(f"9-Point FFT at {selected_time} | Spindle: {spindle_rpm:.0f} RPM ({f_spindle:.1f} Hz base)")
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Amplitude')
    ax.grid(True, alpha=0.5)
    
    max_f_lim = np.nanmax(freqs)
    if np.isnan(max_f_lim): max_f_lim = 0
    ax.set_xlim(0, max_f_lim + 50)
    
    fig_fft.tight_layout()
    st.pyplot(fig_fft)

else:
    st.info("Please upload both CSV files in the sidebar to begin analysis.")
