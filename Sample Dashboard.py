import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


# Load the Hypothetical Data
df = pd.read_excel("Hypothetical_Data.xlsx")


# Streamlit Layout
st.set_page_config(page_title="SDG Dashboard", layout="wide")

st.markdown(
    f"<p style='font-size:65px; color:#5992C6; font-weight:bold;'>"
    f"Drivers of Life Expectancy ❤️"
    f"</p>",
    unsafe_allow_html=True
    )


# Slider (Time Filter)
selected_year = st.slider(
    "Select Year",
    int(df["Year"].min()),
    int(df["Year"].max()),
    2010
)

filtered_df = df[df["Year"] == selected_year]


# KPI Section
st.subheader(f"Key Indicators by Country ({selected_year})")

df_year = df[df["Year"] == selected_year]

avg_life = df_year["Life Expectancy"].mean()
avg_gdp = df_year["GDP per Capita"].mean()
avg_edu = df_year["Education Index"].mean()
avg_hea = df_year["Health Index"].mean()

# Presenting the KPIs withouth Loop
st.markdown(f"### Average KPIs for {selected_year}")
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Avg Life Expectancy",
    f"{avg_life:.2f}"
)

col2.metric(
    "Avg GDP per Capita",
    f"{avg_gdp:.0f}"
)

col3.metric(
    "Avg Education Index",
    f"{avg_edu:.2f}"
)

col4.metric(
    "Avg Health Index",
    f"{avg_hea:.2f}"
)


# Presenting the KPIs with Loop
for _, row in df_year.iterrows():

    st.markdown(f"## {row['Country']}")

    col5, col6, col7, col8 = st.columns(4)

    col5.markdown("##### Life Expectancy")
    col5.markdown(
    f"<p style='font-size:28px; color:#E9B8C9; font-weight:bold;'>"
    f"{row['Life Expectancy']:.2f}"
    f"</p>",
    unsafe_allow_html=True
    )

    col6.markdown("##### GDP Per Capita")
    col6.markdown(
    f"<p style='font-size:28px; color:#93C193; font-weight:bold;'>"
    f"{row['GDP per Capita']:.2f}"
    f"</p>",
    unsafe_allow_html=True
    )

    col7.markdown("##### Education Index")
    col7.markdown(
    f"<p style='font-size:28px; color:#F5CD6A; font-weight:bold;'>"
    f"{row['Education Index']:.2f}"
    f"</p>",
    unsafe_allow_html=True
    )

    col8.markdown("##### Health Index")
    col8.markdown(
    f"<p style='font-size:28px; color:#EB8F48; font-weight:bold;'>"
    f"{row['Health Index']:.2f}"
    f"</p>",
    unsafe_allow_html=True
    )

st.text("")

# Line Chart (Trend Over Time)
st.markdown(
    f"<p style='font-size:45px; color:#F3EDE0; font-weight:bold;'>"
    f"Life Expectancy Trend Over Time"
    f"</p>",
    unsafe_allow_html=True
    )

trend = df.groupby("Year")["Life Expectancy"].mean().reset_index()

fig_line = px.line(
    trend,
    x="Year",
    y="Life Expectancy",
    title="Global Trend"
)

st.plotly_chart(fig_line, use_container_width=True)

st.text("")

# Bar Chart (Country Comparison)
st.markdown(
    f"<p style='font-size:45px; color:#5992C6; font-weight:bold;'>"
    f"Life Expectancy Comparison for {selected_year}"
    f"</p>",
    unsafe_allow_html=True
    )

fig_bar = px.bar(
    filtered_df,
    x="Country",
    y="Life Expectancy",
    color="Country",
    title="Life Expectancy by Country"
)

st.plotly_chart(fig_bar, use_container_width=True)

st.text("")

# Scatter Plot (Drivers)
st.subheader("Relationship: GDP vs Life Expectancy")

fig_scatter = px.scatter(
    df,
    x="GDP per Capita",
    y="Life Expectancy",
    color="Country",
    trendline="ols",
    title="GDP vs Life Expectancy"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.text("")

# Additional Visual (Bubble Chart)
st.subheader("Multi-variable View")

fig_bubble = px.scatter(
    filtered_df,
    x="GDP per Capita",
    y="Life Expectancy",
    size="Education Index",
    color="Country",
    hover_name="Country",
    title="GDP, Education, and Life Expectancy"
)

st.plotly_chart(fig_bubble, use_container_width=True)


# Footer
st.markdown("### 💡 Insight")
st.write(
    "Higher GDP and education levels tend to be associated with higher life expectancy, "
    "though other factors also play a role."
)