import streamlit as st
import pandas as pd

st.title("Loaded Data")

if "uploaded_files" in st.session_state and st.session_state["uploaded_files"]:
    if "loaded_data" not in st.session_state or st.session_state["loaded_data"] is None:
        st.session_state["loaded_data"] = {}

    for file in st.session_state["uploaded_files"]:
        try:
            file_data = file.getvalue()
            df = pd.read_csv(pd.io.common.BytesIO(file_data), delimiter=";", encoding="utf-8")
            st.session_state["loaded_data"][file.name] = df  # ✅ Store loaded data

            st.subheader(f"📄 {file.name}")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Could not load {file.name}: {e}")

elif "loaded_data" in st.session_state and st.session_state["loaded_data"]:
    st.session_state["loaded_data"] = None  # ✅ Clears the stored data when files are cleared
    st.info("No files uploaded yet. Go to the Home page to upload files.")

else:
    st.info("No files uploaded yet. Go to the Home page to upload files.")
