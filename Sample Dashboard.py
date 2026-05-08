import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64

# ==========================================
# 1. CONFIGURATION & THEMING
# ==========================================
st.set_page_config(
    page_title="SDG Dashboard - Life Expectancy Drivers",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

def apply_pro_theme(bg_file):
    bin_str = get_base64(bg_file)
    bg_style = f'url("data:image/jpg;base64,{bin_str}")' if bin_str else "none"
    
    theme_css = f'''
    <style>
    .stApp {{
        background: linear-gradient(135deg, rgba(8, 12, 25, 0.95) 0%, rgba(15, 25, 45, 0.92) 100%),
                    {bg_style};
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }}
    
    [data-testid="stSidebar"] {{
        background: rgba(10, 20, 35, 0.75) !important;
        backdrop-filter: blur(12px);
        border-right: 1px solid rgba(0, 212, 255, 0.2);
    }}
    
    div[data-testid="column"] {{
        background: rgba(20, 30, 50, 0.55);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 18px;
        border: 1px solid rgba(0, 212, 255, 0.15);
    }}
    
    .main-header {{
        background: linear-gradient(90deg, rgba(89, 146, 198, 0.15), rgba(0, 100, 150, 0.08));
        padding: 12px 24px;
        border-radius: 12px;
        border-left: 3px solid #5992C6;
        margin-bottom: 25px;
    }}
    
    .metric-value {{
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #5992C6, #00aaff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
    }}
    
    .metric-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #8a9bb0 !important;
    }}
    
    .selected-info {{
        background: linear-gradient(135deg, rgba(89, 146, 198, 0.15), rgba(0, 100, 150, 0.08));
        border-radius: 12px;
        padding: 15px;
        border-left: 4px solid #5992C6;
        margin-bottom: 15px;
    }}
    
    .insight-card {{
        background: rgba(89, 146, 198, 0.08);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #5992C6;
        margin: 15px 0;
    }}
    </style>
    '''
    st.markdown(theme_css, unsafe_allow_html=True)

# Try to apply theme with background image (optional)
try:
    apply_pro_theme("for trial.jpg")  # Remove or replace with your image
except:
    apply_pro_theme("")  # Fallback to no image

# ==========================================
# 2. DATA ENGINE
# ==========================================
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Hypothetical_Data.xlsx")
        
        # Data validation
        required_cols = ['Country', 'Year', 'GDP per Capita', 'Education Index', 'Health Index', 'Life Expectancy']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return None
        
        # Create normalized indices (0-1 scale) for visualizations
        df['Education Index Normalized'] = df['Education Index'] / 100
        df['Health Index Normalized'] = df['Health Index'] / 100
        
        # Calculate composite SDG Index (average of normalized indices)
        df['SDG Index'] = (df['Education Index Normalized'] + df['Health Index Normalized']) / 2
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

df = load_data()

if df is None:
    st.stop()

# Get unique values for filters
countries = sorted(df["Country"].unique())
years = sorted(df["Year"].unique())

# ==========================================
# 3. SIDEBAR NAVIGATION (Native Streamlit)
# ==========================================
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    # Navigation using radio buttons (alternative to option_menu)
    selected = st.radio(
        "Select View",
        options=["📊 DASHBOARD", "🏔️ COUNTRY ANALYSIS", "🔬 DRIVERS ANALYSIS", 
                 "📈 TRENDS & FORECAST", "📊 COMPARATIVE STUDY", "💡 INSIGHTS"],
        label_visibility="collapsed"
    )
    
    # Remove the emoji prefix for internal use
    selected = selected.split(" ", 1)[-1] if " " in selected else selected
    
    st.divider()
    
    st.markdown("### ⏱️ TIME & FILTERS")
    
    # Year range filter
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    
    # Country multiselect
    selected_countries = st.multiselect(
        "Select Countries",
        options=countries,
        default=countries[:4] if len(countries) >= 4 else countries,
        help="Filter to specific countries for detailed analysis"
    )
    
    # Optional metric threshold
    st.markdown("### 🎯 PERFORMANCE THRESHOLD")
    min_life_expectancy = st.slider("Minimum Life Expectancy", 50, 80, 55)

# Filter data based on selections
filtered_df = df[(df['Year'].between(year_range[0], year_range[1])) & 
                  (df['Life Expectancy'] >= min_life_expectancy)]

if selected_countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]

# ==========================================
# 4. MAIN CONTENT
# ==========================================
st.markdown("""
<div class='main-header'>
    <h1>❤️ Drivers of Life Expectancy Dashboard</h1>
    <p style='margin:0; opacity:0.8;'>Exploring the relationship between socio-economic factors and global health outcomes (2000-2020)</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DASHBOARD VIEW
# ==========================================
if selected == "DASHBOARD":
    # --- KPI SECTION ---
    yearly_data = filtered_df.groupby('Year')['Life Expectancy'].mean().reset_index()
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)
    
    if not yearly_data.empty:
        latest_life = yearly_data['Life Expectancy'].iloc[-1]
        with kpi_col1:
            st.markdown(f"<div style='text-align:center'><span class='metric-label'>GLOBAL AVG LIFE</span><br><span class='metric-value'>{latest_life:.1f} yrs</span></div>", unsafe_allow_html=True)
    
    # Calculate improvement rate
    if len(yearly_data) > 5:
        early_period = yearly_data.head(len(yearly_data)//2)['Life Expectancy'].mean()
        recent_period = yearly_data.tail(len(yearly_data)//2)['Life Expectancy'].mean()
        improvement = recent_period - early_period
        with kpi_col2:
            st.markdown(f"<div style='text-align:center'><span class='metric-label'>IMPROVEMENT RATE</span><br><span class='metric-value'>{improvement:+.1f} yrs</span></div>", unsafe_allow_html=True)
    
    # GDP per capita average
    avg_gdp = filtered_df['GDP per Capita'].mean()
    with kpi_col3:
        st.markdown(f"<div style='text-align:center'><span class='metric-label'>AVG GDP/CAPITA</span><br><span class='metric-value'>${avg_gdp:,.0f}</span></div>", unsafe_allow_html=True)
    
    # Education Index
    avg_edu = filtered_df['Education Index'].mean()
    with kpi_col4:
        st.markdown(f"<div style='text-align:center'><span class='metric-label'>AVG EDUCATION</span><br><span class='metric-value'>{avg_edu:.1f}</span></div>", unsafe_allow_html=True)
    
    # Countries tracked
    with kpi_col5:
        st.markdown(f"<div style='text-align:center'><span class='metric-label'>COUNTRIES</span><br><span class='metric-value'>{filtered_df['Country'].nunique()}</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Top & Bottom Performers
    st.markdown("### 🌍 Country Performance Rankings")
    
    col_top, col_bottom = st.columns(2)
    
    # Get average life expectancy per country (latest year)
    latest_year_data = filtered_df[filtered_df['Year'] == filtered_df['Year'].max()]
    country_avg = latest_year_data.groupby('Country')['Life Expectancy'].mean().reset_index()
    country_avg = country_avg.dropna()
    
    top_performers = country_avg.nlargest(5, 'Life Expectancy')[['Country', 'Life Expectancy']]
    bottom_performers = country_avg.nsmallest(5, 'Life Expectancy')[['Country', 'Life Expectancy']]
    
    with col_top:
        st.markdown("#### 🏆 Top 5 Countries (Highest Life Expectancy)")
        fig_top = px.bar(
            top_performers, 
            x='Life Expectancy', 
            y='Country',
            orientation='h',
            title="Highest Life Expectancy",
            color='Life Expectancy',
            color_continuous_scale='Greens',
            template="plotly_dark",
            labels={'Life Expectancy': 'Life Expectancy (years)', 'Country': ''}
        )
        fig_top.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_top, use_container_width=True)
    
    with col_bottom:
        st.markdown("#### 📉 Bottom 5 Countries (Lowest Life Expectancy)")
        fig_bottom = px.bar(
            bottom_performers, 
            x='Life Expectancy', 
            y='Country',
            orientation='h',
            title="Lowest Life Expectancy",
            color='Life Expectancy',
            color_continuous_scale='Reds',
            template="plotly_dark",
            labels={'Life Expectancy': 'Life Expectancy (years)', 'Country': ''}
        )
        fig_bottom.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bottom, use_container_width=True)
    
    st.markdown("---")
    
    # Global Life Expectancy Trend
    st.markdown("### 📈 GLOBAL LIFE EXPECTANCY TREND")
    fig_trend = px.line(yearly_data, x='Year', y='Life Expectancy', 
                        title="Global Life Expectancy Trend",
                        labels={'Life Expectancy': 'Life Expectancy (years)', 'Year': 'Year'},
                        color_discrete_sequence=['#5992C6'])
    
    # Add trend line
    if len(yearly_data) > 1:
        z = np.polyfit(yearly_data['Year'], yearly_data['Life Expectancy'], 1)
        trend_line = np.poly1d(z)
        fig_trend.add_trace(go.Scatter(
            x=yearly_data['Year'],
            y=trend_line(yearly_data['Year']),
            name=f"Trend (+{z[0]:.3f} years/year)",
            line=dict(color='#ff4444', width=2, dash='dash')
        ))
    
    fig_trend.update_layout(
        template="plotly_dark", 
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        height=500
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Correlation Heatmap
    st.markdown("---")
    st.markdown("### 🔥 Correlation Matrix")
    
    latest_data = filtered_df[filtered_df['Year'] == filtered_df['Year'].max()]
    corr_metrics = ['Life Expectancy', 'GDP per Capita', 'Education Index', 'Health Index']
    corr_matrix = latest_data[corr_metrics].corr()
    
    fig_heatmap = px.imshow(
        corr_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title=f"Correlation Matrix - Latest Year",
        template="plotly_dark",
        zmin=-1, zmax=1
    )
    fig_heatmap.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ==========================================
# COUNTRY ANALYSIS VIEW
# ==========================================
elif selected == "COUNTRY ANALYSIS":
    st.markdown("### 🏔️ COUNTRY-SPECIFIC ANALYSIS")
    
    selected_country_detail = st.selectbox("Select Country for Detailed Analysis", countries)
    
    country_data = filtered_df[filtered_df['Country'] == selected_country_detail].copy()
    
    if not country_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_life = country_data['Life Expectancy'].mean()
            st.metric("Average Life Expectancy", f"{avg_life:.1f} years")
        
        with col2:
            latest_life = country_data['Life Expectancy'].iloc[-1]
            first_life = country_data['Life Expectancy'].iloc[0]
            improvement = latest_life - first_life
            st.metric(f"Life Expectancy Change ({year_range[0]}-{year_range[1]})", f"{improvement:+.1f} years")
        
        with col3:
            avg_gdp = country_data['GDP per Capita'].mean()
            st.metric("Average GDP per Capita", f"${avg_gdp:,.0f}")
        
        with col4:
            latest_edu = country_data['Education Index'].iloc[-1]
            st.metric("Latest Education Index", f"{latest_edu:.1f}")
        
        # Life Expectancy Trend with GDP overlay
        fig_country = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_country.add_trace(
            go.Scatter(x=country_data['Year'], y=country_data['Life Expectancy'],
                      name="Life Expectancy", line=dict(color='#5992C6', width=2)),
            secondary_y=False
        )
        
        fig_country.add_trace(
            go.Scatter(x=country_data['Year'], y=country_data['GDP per Capita'],
                      name="GDP per Capita", line=dict(color='#ff8c00', width=2, dash='dash')),
            secondary_y=True
        )
        
        fig_country.update_layout(
            title=f"Life Expectancy & GDP Trends - {selected_country_detail}",
            template="plotly_dark",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            hovermode='x unified'
        )
        fig_country.update_yaxes(title_text="Life Expectancy (years)", secondary_y=False)
        fig_country.update_yaxes(title_text="GDP per Capita (USD)", secondary_y=True)
        
        st.plotly_chart(fig_country, use_container_width=True)
        
        # Indicators over time
        st.markdown("#### 📊 Key Indicators Evolution")
        
        fig_indicators = px.line(country_data, x='Year', y=['Education Index', 'Health Index'],
                                 title="Education & Health Indices Over Time",
                                 template="plotly_dark",
                                 color_discrete_sequence=['#00d4ff', '#ff8c00'])
        fig_indicators.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_indicators, use_container_width=True)
        
        # Yearly data table
        with st.expander("📊 View Historical Data"):
            display_cols = ['Year', 'Life Expectancy', 'GDP per Capita', 'Education Index', 'Health Index']
            st.dataframe(country_data[display_cols].round(2).sort_values('Year', ascending=False), 
                        use_container_width=True)
    else:
        st.warning(f"No data available for {selected_country_detail} in the selected range")

# ==========================================
# DRIVERS ANALYSIS VIEW
# ==========================================
elif selected == "DRIVERS ANALYSIS":
    st.markdown("### 🔬 DRIVERS OF LIFE EXPECTANCY")
    
    col_scatter1, col_scatter2 = st.columns(2)
    
    with col_scatter1:
        # GDP vs Life Expectancy
        fig_gdp = px.scatter(
            filtered_df,
            x="GDP per Capita",
            y="Life Expectancy",
            color="Country" if selected_countries and len(selected_countries) <= 10 else None,
            size="Health Index",
            hover_data=['Year', 'Education Index'],
            trendline="ols",
            title="GDP per Capita vs Life Expectancy",
            labels={"GDP per Capita": "GDP per Capita (USD)", "Life Expectancy": "Life Expectancy (years)"},
            log_x=True,
            template="plotly_dark"
        )
        fig_gdp.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gdp, use_container_width=True)
    
    with col_scatter2:
        # Education vs Life Expectancy
        fig_edu = px.scatter(
            filtered_df,
            x="Education Index",
            y="Life Expectancy",
            color="Country" if selected_countries and len(selected_countries) <= 10 else None,
            size="GDP per Capita",
            hover_data=['Year', 'Health Index'],
            trendline="ols",
            title="Education Index vs Life Expectancy",
            labels={"Education Index": "Education Index (0-100)", "Life Expectancy": "Life Expectancy (years)"},
            template="plotly_dark"
        )
        fig_edu.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_edu, use_container_width=True)
    
    # 3D Visualization
    st.markdown("---")
    st.markdown("### 🎯 Multi-Dimensional Analysis (3D View)")
    
    latest_data = filtered_df[filtered_df['Year'] == filtered_df['Year'].max()]
    
    fig_3d = px.scatter_3d(
        latest_data,
        x='GDP per Capita',
        y='Education Index',
        z='Life Expectancy',
        color='Country',
        size='Health Index',
        hover_name='Country',
        title='3D: GDP, Education & Life Expectancy Relationship',
        labels={
            'GDP per Capita': 'GDP per Capita (USD)',
            'Education Index': 'Education Index',
            'Life Expectancy': 'Life Expectancy (years)'
        },
        template="plotly_dark",
        log_x=True
    )
    
    fig_3d.update_layout(
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        scene=dict(
            xaxis_title="GDP per Capita (USD)",
            yaxis_title="Education Index",
            zaxis_title="Life Expectancy (years)"
        )
    )
    st.plotly_chart(fig_3d, use_container_width=True)
    
    # Driver Importance Analysis (using numpy instead of sklearn)
    st.markdown("---")
    st.markdown("### 📊 Driver Impact Analysis")
    
    if len(latest_data) > 5:
        # Calculate correlation coefficients as a proxy for impact
        impact_df = pd.DataFrame({
            'Driver': ['GDP per Capita', 'Education Index', 'Health Index'],
            'Correlation with Life Expectancy': [
                latest_data['GDP per Capita'].corr(latest_data['Life Expectancy']),
                latest_data['Education Index'].corr(latest_data['Life Expectancy']),
                latest_data['Health Index'].corr(latest_data['Life Expectancy'])
            ]
        }).sort_values('Correlation with Life Expectancy', ascending=True)
        
        fig_importance = px.bar(impact_df, 
                                x='Correlation with Life Expectancy', 
                                y='Driver', 
                                orientation='h',
                                title="Correlation of Different Drivers with Life Expectancy",
                                color='Correlation with Life Expectancy',
                                color_continuous_scale='Viridis',
                                template="plotly_dark",
                                text='Correlation with Life Expectancy')
        fig_importance.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_importance.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_importance, use_container_width=True)
        
        # Calculate simple linear regression coefficients manually
        X_gdp = latest_data['GDP per Capita'].values.reshape(-1, 1)
        y = latest_data['Life Expectancy'].values
        
        # Simple slope calculation for each driver
        slopes = {}
        for driver in ['GDP per Capita', 'Education Index', 'Health Index']:
            x = latest_data[driver].values
            if len(x) > 1 and x.std() > 0:
                slope = np.corrcoef(x, y)[0, 1] * (y.std() / x.std())
                slopes[driver] = slope
        
        best_driver = max(slopes, key=slopes.get) if slopes else "Education Index"
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>📈 Driver Impact Analysis:</strong><br>
            • <strong>{best_driver}</strong> shows the strongest positive correlation with life expectancy<br>
            • Education and Health indices together explain significant variation in life expectancy<br>
            • GDP per capita positively correlates with longevity, but other factors matter more<br>
            • Countries investing in education and healthcare see better health outcomes
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TRENDS & FORECAST VIEW
# ==========================================
elif selected == "TRENDS & FORECAST":
    st.markdown("### 🔮 PREDICTIVE ANALYSIS & FORECASTING")
    
    yearly_global = filtered_df.groupby('Year')['Life Expectancy'].mean().reset_index()
    
    col_model, col_pred = st.columns(2)
    
    with col_model:
        st.markdown("#### Model Parameters")
        forecast_years = st.slider("Forecast Horizon (Years)", 5, 30, 10)
        confidence_level = st.select_slider("Confidence Interval", options=[80, 85, 90, 95], value=95)
        
        if len(yearly_global) > 1:
            # Weighted regression
            weights = np.exp(np.linspace(0, 1.5, len(yearly_global)))
            weights = weights / weights.sum()
            z = np.polyfit(yearly_global['Year'], yearly_global['Life Expectancy'], 1, w=weights)
            p = np.poly1d(z)
            
            last_year = yearly_global['Year'].iloc[-1]
            future_years = np.arange(last_year + 1, last_year + forecast_years + 1)
            future_life = p(future_years)
            
            residuals = yearly_global['Life Expectancy'] - p(yearly_global['Year'])
            std_residual = residuals.std()
            z_score = 1.96 if confidence_level >= 95 else 1.64 if confidence_level >= 90 else 1.28
            
            st.metric("Projected Improvement Rate", f"{z[0]:+.4f} years/year")
            if 2030 <= future_years[-1]:
                st.metric("Life Expectancy by 2030", f"{p(2030):.1f} years")
            if 2050 <= future_years[-1]:
                st.metric("Life Expectancy by 2050", f"{p(2050):.1f} years")
    
    with col_pred:
        if len(yearly_global) > 1:
            st.markdown("#### 📈 Life Expectancy Projection")
            
            fig_forecast = go.Figure()
            
            fig_forecast.add_trace(go.Scatter(
                x=yearly_global['Year'], y=yearly_global['Life Expectancy'],
                name="Historical Data",
                line=dict(color='#5992C6', width=2),
                mode='lines+markers'
            ))
            
            historical_trend = p(yearly_global['Year'])
            fig_forecast.add_trace(go.Scatter(
                x=yearly_global['Year'], y=historical_trend,
                name="Historical Trend",
                line=dict(color='#ff8c00', width=1.5, dash='dot'),
                opacity=0.7
            ))
            
            fig_forecast.add_trace(go.Scatter(
                x=future_years, y=future_life,
                name=f"Forecast ({forecast_years} years)",
                line=dict(color='#ff4444', width=2.5, dash='dash')
            ))
            
            upper_band = future_life + (z_score * std_residual)
            lower_band = future_life - (z_score * std_residual)
            
            fig_forecast.add_trace(go.Scatter(
                x=np.concatenate([future_years, future_years[::-1]]),
                y=np.concatenate([upper_band, lower_band[::-1]]),
                fill='toself',
                fillcolor='rgba(255, 68, 68, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name=f'{confidence_level}% Confidence Interval'
            ))
            
            fig_forecast.update_layout(
                title=f"Global Life Expectancy Forecast to {future_years[-1]:.0f}",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                height=450,
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_forecast, use_container_width=True)
    
    if len(yearly_global) > 1:
        st.markdown("---")
        st.markdown("### 📅 Forecast Summary")
        
        forecast_table = pd.DataFrame({
            'Year': future_years.astype(int),
            'Projected Life Expectancy (years)': future_life.round(2),
            'Year-over-Year Change (years)': np.append([0], np.diff(future_life).round(4))
        })
        
        display_table = forecast_table.iloc[::max(1, len(forecast_table)//10)].copy()
        
        st.dataframe(display_table, use_container_width=True)

# ==========================================
# COMPARATIVE STUDY VIEW
# ==========================================
elif selected == "COMPARATIVE STUDY":
    st.markdown("### 📊 COUNTRY COMPARISON & BENCHMARKING")
    
    if len(selected_countries) >= 2:
        comparison_data = filtered_df[filtered_df['Country'].isin(selected_countries)]
        
        # Comparison Chart
        fig_comparison = px.line(comparison_data, x='Year', y='Life Expectancy', 
                                 color='Country',
                                 title="Life Expectancy Comparison Across Selected Countries",
                                 template="plotly_dark",
                                 markers=True)
        fig_comparison.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Radar Chart for Latest Year
        st.markdown("#### 🎯 Multi-Metric Comparison (Latest Year)")
        
        latest_comp = comparison_data[comparison_data['Year'] == comparison_data['Year'].max()]
        
        # Get max values for normalization
        max_life = latest_comp['Life Expectancy'].max()
        max_gdp = latest_comp['GDP per Capita'].max()
        
        fig_radar = go.Figure()
        
        for country in selected_countries:
            country_data = latest_comp[latest_comp['Country'] == country]
            if not country_data.empty:
                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        country_data['Life Expectancy'].iloc[0] / max_life,
                        country_data['GDP per Capita'].iloc[0] / max_gdp,
                        country_data['Education Index'].iloc[0] / 100,
                        country_data['Health Index'].iloc[0] / 100,
                        country_data['SDG Index'].iloc[0]
                    ],
                    theta=['Life Expectancy', 'GDP per Capita', 'Education', 'Health', 'SDG Index'],
                    fill='toself',
                    name=country
                ))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title="Normalized Metrics Comparison (0-1 scale)",
            template="plotly_dark",
            height=500,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_radar, use_container_width=True)
        
        # Comparative Statistics Table
        st.markdown("#### 📋 Comparative Statistics")
        
        stats_table = comparison_data.groupby('Country').agg({
            'Life Expectancy': ['mean', 'std', 'min', 'max'],
            'GDP per Capita': 'mean',
            'Education Index': 'mean',
            'Health Index': 'mean'
        }).round(2)
        
        stats_table.columns = ['Life (Mean)', 'Life (Std)', 'Life (Min)', 'Life (Max)', 
                               'GDP (Mean)', 'Education (Mean)', 'Health (Mean)']
        
        st.dataframe(stats_table, use_container_width=True)
        
    else:
        st.warning("⚠️ Please select at least 2 countries in the sidebar for comparison")

# ==========================================
# INSIGHTS VIEW
# ==========================================
elif selected == "INSIGHTS":
    st.markdown("### 📊 KEY FINDINGS & RECOMMENDATIONS")
    
    tab1, tab2, tab3 = st.tabs(["📈 Trend Analysis", "📊 Statistical Summary", "💡 Strategic Insights"])
    
    with tab1:
        st.markdown("#### Decadal Analysis")
        
        filtered_df['Decade'] = (filtered_df['Year'] // 10) * 10
        decadal_stats = filtered_df.groupby('Decade').agg({
            'Life Expectancy': ['mean', 'std', 'min', 'max'],
            'GDP per Capita': 'mean',
            'Education Index': 'mean',
            'Health Index': 'mean'
        }).round(2)
        
        decadal_stats.columns = ['Life Mean (yrs)', 'Life Std', 'Life Min', 'Life Max',
                                 'GDP Mean ($)', 'Education Mean', 'Health Mean']
        st.dataframe(decadal_stats, use_container_width=True)
        
        if len(decadal_stats) > 1:
            decadal_changes = decadal_stats['Life Mean (yrs)'].diff().dropna()
            
            fig_decadal = px.bar(
                x=decadal_changes.index, y=decadal_changes.values,
                labels={'x': 'Decade', 'y': 'Life Expectancy Improvement (years)'},
                title="Decadal Improvement in Life Expectancy",
                color=decadal_changes.values,
                color_continuous_scale='RdYlGn',
                template="plotly_dark"
            )
            fig_decadal.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_decadal, use_container_width=True)
    
    with tab2:
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            st.markdown("#### Distribution Analysis")
            fig_hist = px.histogram(
                filtered_df, x='Life Expectancy',
                nbins=30, title="Life Expectancy Distribution",
                color_discrete_sequence=['#5992C6'],
                template="plotly_dark",
                marginal='box'
            )
            fig_hist.update_layout(paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col_stats2:
            st.markdown("#### Summary Statistics")
            stats_df = filtered_df[['Life Expectancy', 'GDP per Capita', 'Education Index', 'Health Index']].describe().round(2)
            st.dataframe(stats_df, use_container_width=True)
    
    with tab3:
        st.markdown("""
        <div class="insight-card">
            <h4>🔑 Key Findings</h4>
            <ul>
                <li><strong>Strong Correlation:</strong> Countries with higher GDP, education, and health indices consistently show higher life expectancy</li>
                <li><strong>Education is Key:</strong> Education index shows the strongest correlation with life expectancy improvements</li>
                <li><strong>Health Investment Matters:</strong> Health index is a significant predictor of longevity, especially in developing nations</li>
                <li><strong>Regional Disparities:</strong> Significant gaps exist between best and worst performing countries</li>
                <li><strong>Improvement Trajectory:</strong> Most countries show positive trends, but at varying rates</li>
            </ul>
        </div>
        
        <div class="insight-card">
            <h4>🚀 Strategic Recommendations</h4>
            <ul>
                <li><strong>For Policymakers:</strong> Prioritize education and healthcare infrastructure investments</li>
                <li><strong>For International Organizations:</strong> Target assistance to countries with low education/health indices</li>
                <li><strong>For Research:</strong> Further investigate outlier countries for best practices</li>
                <li><strong>For Monitoring:</strong> Track SDG progress using these key indicators</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Additional insights
        if 'top_performers' in locals() and not top_performers.empty:
            st.markdown(f"""
            <div class="insight-card">
                <h4>📈 Top Performing Countries</h4>
                """ + "".join([f"• <strong>{country}</strong>: {life:.1f} years life expectancy<br>" 
                              for country, life in top_performers.head(3).values]) + """
            </div>
            """, unsafe_allow_html=True)
        
        best_year = filtered_df.groupby('Year')['Life Expectancy'].mean().idxmax()
        best_value = filtered_df.groupby('Year')['Life Expectancy'].mean().max()
        st.info(f"🌟 **Peak Performance Year:** {int(best_year)} achieved the highest global average life expectancy of {best_value:.2f} years")

# ==========================================
# FOOTER
# ==========================================
st.markdown("---")
st.caption("📊 SDG Dashboard: Analyzing Drivers of Life Expectancy | Data Source: Hypothetical Dataset (2000-2020) | Built with Streamlit & Plotly")
