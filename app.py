import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import itertools

st.set_page_config(layout="wide")  # ✅ Run Streamlit in wide mode
st.title("Voltammetry Web App")

# ✅ File Upload Section
uploaded_files = st.file_uploader("Upload one or more CV or DPV files", type=["csv", "txt"], accept_multiple_files=True)

# ✅ Scan range input for CV
scan_range = st.text_input("Enter scan range (e.g., '1-5,7' or 'all')", value="all")

# ✅ Function to detect if a file is CV or DPV
def detect_file_type(df):
    if "Scan" in df.columns and "WE(1).Potential (V)" in df.columns and "WE(1).Current (A)" in df.columns:
        return "CV"
    elif "WE(1).Base.Potential (V)" in df.columns and "WE(1).δ.Current (A)" in df.columns:
        return "DPV"
    return "Unknown"

# ✅ Function to process CV files
def process_cv(df, filename, scan_range="all", num_files=1, file_index=0):
    fig = go.Figure()
    color_cycle = itertools.cycle(go.Figure().layout.template.layout.colorway)  
    file_colors = [next(color_cycle) for _ in range(num_files)]  

    df['WE(1).Current (A)'] *= 1e6  # Convert A to µA
    scans = df['Scan'].unique() if "Scan" in df.columns else [1]
    
    for scan in scans:
        x = df[df['Scan'] == scan]['WE(1).Potential (V)']
        y = df[df['Scan'] == scan]['WE(1).Current (A)']
        scan_color = next(color_cycle) if num_files == 1 else file_colors[file_index]

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="lines",
            name=f"{filename} - Scan {scan}",
            line=dict(color=scan_color)
        ))

    fig.update_layout(
        title="Cyclic Voltammetry (CV) Plot",
        xaxis=dict(title="Potential (V)", showline=True, showgrid=True),
        yaxis=dict(title="Current (µA)", showline=True, showgrid=True),
        hovermode="x unified"
    )
    
    return fig

# ✅ Function to process DPV files
def process_dpv(df, filename):
    fig = go.Figure()
    df["WE(1).δ.Current (A)"] *= 1e6  # Convert A to µA

    fig.add_trace(go.Scatter(
        x=df["WE(1).Base.Potential (V)"],
        y=df["WE(1).δ.Current (A)"],
        mode="lines",
        name=filename
    ))

    fig.update_layout(
        title="Differential Pulse Voltammetry (DPV) Plot",
        xaxis=dict(title="Potential (V)", showline=True, showgrid=True),
        yaxis=dict(title="Delta Current (µA)", showline=True, showgrid=True),
        hovermode="x unified"
    )

    return fig

# ✅ Process Files When Button is Clicked
if uploaded_files:
    if st.button("Process"):
        combined_fig = go.Figure()
        num_files = len(uploaded_files)

        for file_index, file in enumerate(uploaded_files):
            df = pd.read_csv(file, delimiter=';', encoding='utf-8')
            file_type = detect_file_type(df)

            if file_type == "CV":
                fig = process_cv(df, file.name, scan_range, num_files, file_index)
            elif file_type == "DPV":
                fig = process_dpv(df, file.name)
            else:
                st.error(f"Skipping {file.name}: Unknown file format.")
                continue

            for trace in fig.data:
                combined_fig.add_trace(trace)

        st.plotly_chart(combined_fig, use_container_width=True, config={"scrollZoom": True})
