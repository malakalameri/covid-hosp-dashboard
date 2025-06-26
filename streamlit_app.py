import pandas as pd
import streamlit as st
import plotly.express as px

@st.cache_data
def load():
    # CSV sits in the repo root
    df = pd.read_csv(
        "Monthly_Rates_of_Laboratory-Confirmed_COVID-19_Hospitalizations_from_the_COVID-NET_Surveillance_System.csv"
    )
    df = df.rename(columns={"_YearMonth": "YearMonth"})
    df["YearMonth"] = pd.to_datetime(df["YearMonth"].astype(int).astype(str), format="%Y%m")
    return df

df = load()

st.set_page_config(page_title="COVID-NET Dashboard", layout="wide")

states = st.sidebar.multiselect("State", sorted(df["State"].unique()), default=["COVID-NET"])
ages   = st.sidebar.multiselect("Age group", sorted(df["AgeCategory_Legend"].unique()))
chart  = st.sidebar.radio("Chart", ["Line", "Area", "Heatmap"], horizontal=True)

data = df[
    df["State"].isin(states) &
    df["AgeCategory_Legend"].isin(ages)
]

if chart == "Line":
    fig = px.line(data, x="YearMonth", y="MonthlyRate", color="State")
elif chart == "Area":
    fig = px.area(data, x="YearMonth", y="MonthlyRate", color="AgeCategory_Legend", groupnorm="percent")
else:
    heat = (data.groupby(["YearMonth", "State"])["MonthlyRate"]
                 .mean()
                 .reset_index()
                 .pivot(index="State", columns="YearMonth", values="MonthlyRate"))
    fig = px.imshow(heat, aspect="auto", labels=dict(x="Month", y="State", color="Rate"))

st.plotly_chart(fig, use_container_width=True)
