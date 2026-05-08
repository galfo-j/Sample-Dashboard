import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="SDG Dashboard - Life Expectancy Drivers",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    .insight-box {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #5992C6;
        margin: 20px 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        border-top: 1px solid #ddd;
        margin-top: 50px;
    }
</style>
""", unsafe_allow_html=True)

# Load data with caching for performance
@st.cache_data
def load_data():
    df = pd.read_excel("Hypothetical_Data.xlsx")
    return df

df = load_data()

# Sidebar filters
with st.sidebar:
    st.markdown("## 🔍 Filters")
    
    # Year range slider
    selected_year = st.slider(
        "Select Year",
        int(df["Year"].min()),
        int(df["Year"].max()),
        2010,
        format="%d"
    )
    
    # Multi-select for countries
    all_countries = df["Country"].unique()
    selected_countries = st.multiselect(
        "Select Countries (Optional)",
        options=all_countries,
        default=all_countries[:5] if len(all_countries) > 5 else all_countries,
        help="Filter to specific countries for detailed analysis"
    )
    
    # Metric selector for trend analysis
    trend_metric = st.selectbox(
        "Select Metric for Trend Analysis",
        options=["Life Expectancy", "GDP per Capita", "Education Index", "Health Index"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📊 About")
    st.info(
        "This dashboard analyzes key drivers affecting life expectancy "
        "including GDP per capita, education, and health indices across "
        "different countries and years."
    )

# Main title with animation effect
st.markdown(
    f"<p style='font-size:65px; color:#5992C6; font-weight:bold; text-align:center;'>"
    f"📈 Drivers of Life Expectancy ❤️"
    f"</p>",
    unsafe_allow_html=True
)
st.markdown("<p style='text-align:center; font-size:18px;'>Exploring the relationship between socio-economic factors and global health outcomes</p>", unsafe_allow_html=True)

# Filter data based on selections
filtered_df = df[df["Year"] == selected_year]
if selected_countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
    trend_df = df[df["Country"].isin(selected_countries)]
else:
    trend_df = df

# KPI Section
st.markdown("---")
st.subheader(f"🎯 Global Key Performance Indicators ({selected_year})")

df_year = df[df["Year"] == selected_year]
avg_life = df_year["Life Expectancy"].mean()
avg_gdp = df_year["GDP per Capita"].mean()
avg_edu = df_year["Education Index"].mean()
avg_hea = df_year["Health Index"].mean()
max_life_country = df_year.loc[df_year["Life Expectancy"].idxmax(), "Country"]
max_life_value = df_year["Life Expectancy"].max()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "📊 Avg Life Expectancy",
        f"{avg_life:.1f} years",
        delta=f"{avg_life - df[df['Year'] == selected_year-1]['Life Expectancy'].mean():.1f} vs prev year" if selected_year > df['Year'].min() else None
    )

with col2:
    st.metric(
        "💰 Avg GDP per Capita",
        f"${avg_gdp:,.0f}",
        delta=f"{((avg_gdp - df[df['Year'] == selected_year-1]['GDP per Capita'].mean())/df[df['Year'] == selected_year-1]['GDP per Capita'].mean()*100):.1f}%" if selected_year > df['Year'].min() else None
    )

with col3:
    st.metric(
        "🎓 Avg Education Index",
        f"{avg_edu:.2f}",
        delta=f"{avg_edu - df[df['Year'] == selected_year-1]['Education Index'].mean():.2f}" if selected_year > df['Year'].min() else None
    )

with col4:
    st.metric(
        "🏥 Avg Health Index",
        f"{avg_hea:.2f}",
        delta=f"{avg_hea - df[df['Year'] == selected_year-1]['Health Index'].mean():.2f}" if selected_year > df['Year'].min() else None
    )

with col5:
    st.metric(
        "🏆 Highest Life Expectancy",
        f"{max_life_value:.1f} years",
        delta=max_life_country
    )

# Detailed country metrics
if not filtered_df.empty and len(filtered_df) <= 20:  # Only show detailed view if not too many countries
    st.markdown("---")
    st.subheader(f"📋 Detailed Country Metrics ({selected_year})")
    
    # Create a more efficient display using expanders
    for idx, (_, row) in enumerate(filtered_df.iterrows()):
        with st.expander(f"📍 {row['Country']} - Detailed Metrics"):
            col_a, col_b, col_c, col_d = st.columns(4)
            
            with col_a:
                st.markdown("**Life Expectancy**")
                st.markdown(f"<span style='font-size:32px; color:#E9B8C9; font-weight:bold;'>{row['Life Expectancy']:.1f}</span> years", unsafe_allow_html=True)
                
            with col_b:
                st.markdown("**GDP Per Capita**")
                st.markdown(f"<span style='font-size:32px; color:#93C193; font-weight:bold;'>${row['GDP per Capita']:,.0f}</span>", unsafe_allow_html=True)
                
            with col_c:
                st.markdown("**Education Index**")
                progress = row['Education Index'] / 1.0
                st.progress(progress, text=f"{row['Education Index']:.2f} / 1.00")
                
            with col_d:
                st.markdown("**Health Index**")
                progress = row['Health Index'] / 1.0
                st.progress(progress, text=f"{row['Health Index']:.2f} / 1.00")

st.markdown("---")

# Visualization section with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends Over Time", "🏆 Country Comparison", "🔬 Correlation Analysis", "🎯 Multi-Dimensional View"])

with tab1:
    st.markdown(f"### {trend_metric} Trends Over Time")
    
    # Line chart with multiple countries or global trend
    if selected_countries and len(selected_countries) <= 10:
        trend_data = trend_df.groupby(["Year", "Country"])[trend_metric].mean().reset_index()
        fig_line = px.line(
            trend_data,
            x="Year",
            y=trend_metric,
            color="Country",
            title=f"{trend_metric} Trends by Country",
            markers=True,
            line_shape="linear"
        )
    else:
        trend_data = df.groupby("Year")[trend_metric].mean().reset_index()
        fig_line = px.line(
            trend_data,
            x="Year",
            y=trend_metric,
            title=f"Global {trend_metric} Trend",
            markers=True,
            line_shape="linear"
        )
    
    fig_line.update_layout(
        hovermode='x unified',
        title_x=0.5,
        xaxis_title="Year",
        yaxis_title=trend_metric
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Year-over-year change
    st.markdown("### 📊 Year-over-Year Change")
    trend_data['YoY Change'] = trend_data[trend_metric].pct_change() * 100
    fig_yoy = px.bar(
        trend_data[trend_data['Year'] > trend_data['Year'].min()],
        x="Year",
        y="YoY Change",
        title=f"Year-over-Year % Change in {trend_metric}",
        color="YoY Change",
        color_continuous_scale="RdYlGn"
    )
    fig_yoy.update_layout(title_x=0.5)
    st.plotly_chart(fig_yoy, use_container_width=True)

with tab2:
    st.markdown(f"### Life Expectancy Comparison ({selected_year})")
    
    # Sort data for better visualization
    sorted_df = filtered_df.sort_values("Life Expectancy", ascending=True)
    
    fig_bar = px.bar(
        sorted_df,
        x="Life Expectancy",
        y="Country",
        orientation='h',
        color="Life Expectancy",
        color_continuous_scale="Viridis",
        title=f"Life Expectancy by Country - {selected_year}",
        text="Life Expectancy",
        height=max(400, len(sorted_df) * 30)
    )
    
    fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_bar.update_layout(title_x=0.5, xaxis_title="Life Expectancy (years)")
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # GDP vs Life Expectancy side by side
    col1, col2 = st.columns(2)
    
    with col1:
        fig_gdp = px.bar(
            sorted_df.head(10),
            x="GDP per Capita",
            y="Country",
            orientation='h',
            color="GDP per Capita",
            color_continuous_scale="Blues",
            title=f"Top 10 Countries by GDP per Capita - {selected_year}"
        )
        fig_gdp.update_layout(title_x=0.5)
        st.plotly_chart(fig_gdp, use_container_width=True)
    
    with col2:
        fig_edu = px.bar(
            sorted_df.head(10),
            x="Education Index",
            y="Country",
            orientation='h',
            color="Education Index",
            color_continuous_scale="Greens",
            title=f"Top 10 Countries by Education Index - {selected_year}"
        )
        fig_edu.update_layout(title_x=0.5)
        st.plotly_chart(fig_edu, use_container_width=True)

with tab3:
    st.markdown("### 📈 Correlation Analysis")
    
    # Scatter plot with trendline
    fig_scatter = px.scatter(
        df if not selected_countries else trend_df,
        x="GDP per Capita",
        y="Life Expectancy",
        color="Country" if selected_countries and len(selected_countries) <= 10 else None,
        size="Health Index",
        hover_data=['Year', 'Education Index'],
        trendline="ols",
        title="GDP per Capita vs Life Expectancy",
        labels={"GDP per Capita": "GDP per Capita (USD)", "Life Expectancy": "Life Expectancy (years)"},
        log_x=True
    )
    
    fig_scatter.update_layout(title_x=0.5)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Correlation matrix heatmap
    st.markdown("### 🔥 Correlation Matrix")
    
    # Calculate correlation matrix for the selected year
    corr_metrics = ['Life Expectancy', 'GDP per Capita', 'Education Index', 'Health Index']
    corr_matrix = df[df['Year'] == selected_year][corr_metrics].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title=f"Correlation Matrix - {selected_year}",
        zmin=-1, zmax=1
    )
    
    fig_heatmap.update_layout(title_x=0.5)
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab4:
    st.markdown(f"### 🎯 Multi-Dimensional View ({selected_year})")
    
    # 3D Scatter plot
    fig_3d = px.scatter_3d(
        filtered_df,
        x='GDP per Capita',
        y='Education Index',
        z='Life Expectancy',
        color='Country',
        size='Health Index',
        hover_name='Country',
        title='3D Visualization: GDP, Education, and Life Expectancy',
        labels={
            'GDP per Capita': 'GDP per Capita (USD)',
            'Education Index': 'Education Index',
            'Life Expectancy': 'Life Expectancy (years)'
        }
    )
    
    fig_3d.update_layout(title_x=0.5, scene=dict(
        xaxis_title="GDP per Capita (USD)",
        yaxis_title="Education Index",
        zaxis_title="Life Expectancy (years)"
    ))
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # Bubble chart
    fig_bubble = px.scatter(
        filtered_df,
        x="GDP per Capita",
        y="Life Expectancy",
        size="Education Index",
        color="Health Index",
        hover_name="Country",
        title="GDP, Education, and Life Expectancy (Bubble Size = Education, Color = Health)",
        labels={
            "GDP per Capita": "GDP per Capita (USD)",
            "Life Expectancy": "Life Expectancy (years)",
            "Education Index": "Education Index",
            "Health Index": "Health Index"
        },
        log_x=True,
        size_max=60
    )
    
    fig_bubble.update_layout(title_x=0.5)
    st.plotly_chart(fig_bubble, use_container_width=True)

# Insights section
st.markdown("---")
st.markdown("## 💡 Key Insights & Recommendations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎯 Major Findings")
    st.markdown("""
    - **Strong GDP-Life Expectancy Correlation**: Countries with higher GDP per capita generally show higher life expectancy
    - **Education Impact**: Education index shows strong positive correlation with health outcomes
    - **Health Index Importance**: Health infrastructure investment correlates with longer life expectancy
    - **Regional Variations**: Significant disparities exist between different countries and regions
    """)

with col2:
    st.markdown("### 🚀 Policy Recommendations")
    st.markdown("""
    - **Invest in Education**: Focus on improving education access and quality
    - **Healthcare Infrastructure**: Increase healthcare spending and access to medical services
    - **Economic Development**: Support economic growth policies that benefit public health
    - **Data-Driven Decisions**: Use these metrics to track progress and adjust strategies
    """)

# Interactive data table
with st.expander("📊 View Raw Data"):
    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=400,
        column_config={
            "Life Expectancy": st.column_config.NumberColumn(format="%.1f"),
            "GDP per Capita": st.column_config.NumberColumn(format="$%.0f"),
            "Education Index": st.column_config.NumberColumn(format="%.2f"),
            "Health Index": st.column_config.NumberColumn(format="%.2f")
        }
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"life_expectancy_data_{selected_year}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown(
    """
    <div class='footer'>
        <p>📊 Data Dashboard for Sustainable Development Goal (SDG) Analysis</p>
        <p>Built with Streamlit, Plotly, and ❤️ | Data source: Hypothetical Dataset</p>
    </div>
    """,
    unsafe_allow_html=True
)
