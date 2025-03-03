import streamlit as st
import plotly.graph_objects as go

st.title("Plotly Axis Title Debugging")

fig = go.Figure()

fig.add_trace(go.Scatter(x=[1, 2, 3], y=[3, 1, 6], mode="lines", name="Test Line"))

fig.update_layout(
    title=dict(text="This is the Plot Title", font=dict(size=20), x=0.5),
    xaxis=dict(title=dict(text="X-Axis Label", font=dict(size=16))),
    yaxis=dict(title=dict(text="Y-Axis Label", font=dict(size=16)))
)

st.plotly_chart(fig)
