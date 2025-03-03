import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import itertools

plot_height = 2500



st.set_page_config(layout="wide")  # ✅ Run Streamlit in wide mode
st.title("Voltammetry Web App")

with st.sidebar:
    st.header("Upload & Settings")
    
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0  # ✅ Create a unique key for the file uploader

    uploaded_files = st.file_uploader("Upload CV/DPV Files", type=["csv", "txt"], accept_multiple_files=True, key=f"uploader_{st.session_state['uploader_key']}")


    scan_range = st.text_input("Scan Range (e.g., '1-3,5' or 'all')", value="all")

    col1, col2 = st.columns([1, 1])  # ✅ Creates two buttons side by side

    with col1:
        process_button = st.button("Process Data")
    
    with col2:
        clear_button = st.button("Clear Files")

if clear_button:
    st.session_state["uploader_key"] += 1  # ✅ Change the key to reset the uploader
    st.session_state["stored_figure"] = None
    st.rerun()  # ✅ Force Streamlit to refresh




# ✅ Function to detect if a file is CV or DPV
def detect_file_type(df):
    if "Scan" in df.columns and "WE(1).Potential (V)" in df.columns and "WE(1).Current (A)" in df.columns:
        return "CV"
    elif "WE(1).Base.Potential (V)" in df.columns and "WE(1).δ.Current (A)" in df.columns:
        return "DPV"
    return "Unknown"

def parse_scan_range(scan_range, available_scans):
    if scan_range.lower() == "all":
        return available_scans

    selected_scans = set()

    try:
        for part in scan_range.split(","):
            part = part.strip()
            if "-" in part:
                start, end = map(int, part.split("-"))
                selected_scans.update(range(start, end + 1))
            else:
                selected_scans.add(int(part))
    except ValueError:
        st.error("Invalid scan range format. Use format like '1-3,5' or 'all'.")

    selected_scans = sorted(set(selected_scans) & set(available_scans))


    return selected_scans


# ✅ Function to process CV files
def process_cv(df, filename, scan_range="all", num_files=1, file_index=0):
    fig = go.Figure()
    color_cycle = itertools.cycle(go.Figure().layout.template.layout.colorway)  
    file_colors = [next(color_cycle) for _ in range(num_files)]  

    df['WE(1).Current (A)'] *= 1e6  # Convert A to µA
    scans = df['Scan'].unique() if "Scan" in df.columns else [1]

    # ✅ Debug: Print detected scan numbers
    #st.write(f"Detected Scans in {filename}: {scans}")

    # ✅ Parse scan range
    selected_scans = parse_scan_range(scan_range, scans)
    #st.write(f"Selected Scans: {selected_scans}")  # ✅ Debug Output

    for scan in selected_scans:
        scan_df = df[df['Scan'] == scan]

        if scan_df.empty:
            st.write(f"Warning: No data found for scan {scan} in {filename}")
            continue

        x = scan_df['WE(1).Potential (V)']
        y = scan_df['WE(1).Current (A)']
        scan_color = next(color_cycle) if num_files == 1 else file_colors[file_index]

        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode="lines",
            name=f"{filename} - Scan {scan}",
            line=dict(color=scan_color)
        ))

    fig.update_layout(
        title={"text": f"Cyclic Voltammetry (CV) - {filename}", "x": 0.5, "font": {"size": 20}},
        xaxis={"title": {"text": "Potential (V)", "font": {"size": 16}}},
        yaxis={"title": {"text": "Current (µA)", "font": {"size": 16}}},
        height=plot_height
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
        hovermode="x unified",
        height=plot_height
    )

    return fig

if "zoom_state" not in st.session_state:
    st.session_state.zoom_state = {}  # Store only zoom-related data

if uploaded_files and process_button:
    combined_fig = go.Figure()
    num_files = len(uploaded_files)

    for file_index, file in enumerate(uploaded_files):
        try:
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

        except Exception as e:
            st.error(f"Error processing {file.name}: {e}")
            continue

    # Forcefully ensure title and axis labels exist in layout
    combined_fig.update_layout(
        title={"text": "Combined Voltammetry Plot", "x": 0.5, "font": {"size": 20}},
        xaxis={"title": {"text": "Potential (V)", "font": {"size": 16}}},
        yaxis={"title": {"text": "Current (µA)", "font": {"size": 16}}}
    )

    # Debugging: Print the updated figure JSON
    #st.write("Updated Figure JSON:")
    #st.json(combined_fig.to_dict())


    # ✅ Display the plot
    st.plotly_chart(combined_fig, use_container_width=False, config={"scrollZoom": True}, height=plot_height)

