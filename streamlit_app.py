import pandas as pd
import streamlit as st
import plotly.express as px

# ---------- DATA ----------
@st.cache_data(show_spinner=False)
def load():
    df = pd.read_csv(
        "Monthly_Rates_of_Laboratory-Confirmed_COVID-19_Hospitalizations_from_the_COVID-NET_Surveillance_System.csv"
    )
    df = df.rename(columns={"_YearMonth": "YearMonth"})
    df["YearMonth"] = pd.to_datetime(df["YearMonth"].astype(int).astype(str), format="%Y%m")
    return df

df = load()

# ---------- PAGE ----------
st.set_page_config(page_title="COVID-NET Dashboard", layout="wide")

# ---------- SIDEBAR FILTERS ----------
state_options = sorted(df["State"].unique())
age_options   = sorted(df["AgeCategory_Legend"].unique())

states = st.sidebar.multiselect(
    "State",
    state_options,
    default=["COVID-NET"]          # national aggregate ticked by default
)

ages = st.sidebar.multiselect(
    "Age group",
    age_options,
    default=age_options            # *everything* pre-selected
)

chart_type = st.sidebar.radio(
    "Chart", ["Line", "Area", "Heatmap"], horizontal=True
)

# fail-safe – if user nukes filters, re-select everything
if not states:
    states = state_options
if not ages:
    ages = age_options

# ---------- FILTERED DATA ----------
data = df[
    df["State"].isin(states) &
    df["AgeCategory_Legend"].isin(ages)
]

# ---------- VISUALS ----------
if chart_type == "Line":
    fig = px.line(
        data,
        x="YearMonth",
        y="MonthlyRate",
        color="State",
        markers=True,
        title="Monthly COVID-19 Hospitalization Rate"
    )

elif chart_type == "Area":
    fig = px.area(
        data,
        x="YearMonth",
        y="MonthlyRate",
        color="AgeCategory_Legend",
        groupnorm="percent",
        title="Share of Hospitalizations by Age Group"
    )

else:  # Heatmap
    heat = (
        data.groupby(["YearMonth", "State"], as_index=False)["MonthlyRate"]
        .mean()
        .pivot(index="State", columns="YearMonth", values="MonthlyRate")
    )
    fig = px.imshow(
        heat,
        aspect="auto",
        labels=dict(x="Month", y="State", color="Rate"),
        title="Heatmap of Monthly Hospitalization Rate"
    )

st.plotly_chart(fig, use_container_width=True)

# ---------- KPI ----------
latest_date = data["YearMonth"].max()
latest_rate = data.loc[data["YearMonth"] == latest_date, "MonthlyRate"].mean()
st.metric("Latest avg. rate", f"{latest_rate:.1f} per 100 k")
