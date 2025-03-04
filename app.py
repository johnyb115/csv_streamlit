import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import itertools
import zipfile
import io

plot_height = 2500


st.set_page_config(layout="wide")


st.title("Voltammetry CSV plotter")

# ✅ Move all controls into the sidebar
with st.sidebar:

    # ✅ Process Data Button (Green Tint)
    process_button = st.markdown(
        """
        <style>
        .stButton>button {
            #background-color: #4CAF50 !important;
            color: white !important;
            width: 100%;
            font-size: 16px;
            padding: 10px;
        }
        </style>
        """, unsafe_allow_html=True
    )
    process_button = st.button("Process Data")

    # ✅ Clear Files Button (Below)
    clear_button = st.button("🗑️ Clear Files")


    st.header("Upload & Settings")

    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 0

    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []

    uploaded_files = st.file_uploader(
        "Upload CV/DPV Files", type=["csv", "txt"], accept_multiple_files=True, 
        key=f"uploader_{st.session_state['uploader_key']}"
    )

    # ✅ Store uploaded files in session state
    if uploaded_files:
        st.session_state["uploaded_files"] = uploaded_files

    # ✅ Show currently uploaded files (if any)
    if "uploaded_files" in st.session_state and st.session_state["uploaded_files"]:
        st.write("### Uploaded Files:")
        for file in st.session_state["uploaded_files"]:
            st.write(f"📄 {file.name}")



    scan_range = st.text_input("Scan Range (e.g., '1-3,5' or 'all')", value="all")


    if clear_button:
        st.session_state["uploader_key"] += 1  # ✅ Resets the file uploader
        st.session_state["stored_figure"] = None  # ✅ Clears the plot
        st.session_state["uploaded_files"] = []  # ✅ Clears uploaded file list
        st.session_state["loaded_data"] = None  # ✅ Clears Loaded Data page content
        st.rerun()  # ✅ Forces Streamlit to refresh


    # ✅ Store processed files
    processed_files = {}

    if st.button("📥 Process & Download All as ZIP"):
        for file in st.session_state["uploaded_files"]:
            output_filename = f"processed_{file.name}"

            # ✅ Read the uploaded CSV
            df = pd.read_csv(file, delimiter=';', encoding='utf-8')

            # ✅ Standard column names expected
            expected_columns = ["Scan", "WE(1).Potential (V)", "WE(1).Current (A)"]

            # ✅ Check if all required columns exist
            if not all(col in df.columns for col in expected_columns):
                st.error(f"Skipping {file.name}: Missing required columns! Found: {df.columns.tolist()}")
                continue

            # ✅ Process the data
            scan_dfs = []
            df["WE(1).Current (A)"] *= 1e6  # Convert A to µA

            for scan in df["Scan"].unique():
                sub_df = df[df["Scan"] == scan][["WE(1).Potential (V)", "WE(1).Current (A)"]].reset_index(drop=True)
                sub_df.columns = [f"Potential_{scan}", f"Current_{scan}"]
                scan_dfs.append(sub_df)

            df_final = pd.concat(scan_dfs, axis=1)

            # ✅ Convert dataframe to CSV and store it
            csv_data = df_final.to_csv(index=False).encode('utf-8')
            processed_files[output_filename] = csv_data

        # ✅ Create ZIP archive if files were processed
        if processed_files:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, data in processed_files.items():
                    zip_file.writestr(filename, data)

            zip_buffer.seek(0)

            # ✅ Provide a download button for the ZIP
            st.download_button(
                label="⬇ Download All Processed Files (ZIP)",
                data=zip_buffer,
                file_name="processed_files.zip",
                mime="application/zip"
            )
        else:
            st.warning("No files were processed. Please check your uploads.")


    
    # ✅ Instruction Bar at Bottom of Sidebar
    st.markdown("---")  # Adds a separator
    st.markdown("### ❓ How to Use:")
    st.markdown("""
    1️⃣ **Load your CSV**  
    2️⃣ **Click Process**  
    3️⃣ **Enjoy the Interactive Plot, Bitch! 🚀**
    """)



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

#What the hell is happening
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

    combined_fig.update_layout(
        title={"text": "Combined Voltammetry Plot", "x": 0.5, "font": {"size": 20}},
        xaxis={"title": {"text": "Potential (V)", "font": {"size": 16}}},
        yaxis={"title": {"text": "Current (µA)", "font": {"size": 16}}}
    )

    # ✅ Store the plot in session state
    st.session_state["stored_figure"] = combined_fig

# ✅ Restore the plot if it exists
if "stored_figure" in st.session_state and st.session_state["stored_figure"] is not None:
    # ✅ Ensure the plot takes the full available space
    st.plotly_chart(
        st.session_state["stored_figure"],
        use_container_width=True,  # ✅ Auto-resizes to fit available space
        config={"scrollZoom": True}
    )
