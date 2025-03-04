import streamlit as st

st.title("About This App")

st.markdown("""
**Voltammetry Web App**  
This application allows users to upload and analyze **Cyclic Voltammetry (CV)** and **Differential Pulse Voltammetry (DPV)** data.
In this state, it is specific to Metrohm NOVA export, but will be modified in the future for more general use.

### Features:
- Upload and process multiple files
- Select scan ranges for CV data
- View raw uploaded data
- Interactive Plotly visualization with zooming and panning
- Built with Python, Streamlit, and Plotly

**Developed by:** *Jan Brodsky / Brno University of Technology*
""")
