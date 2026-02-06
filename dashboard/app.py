import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from db_operations import (
    get_latest_stock_prices,
    get_stock_history,
    get_all_returns,
    get_portfolio_performance,
    get_stock_info
)

# Page configuration
st.set_page_config(
    page_title="Stock Market Analytics",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Tech Stock Market Analytics ")
st.markdown("""
**Automated Pipeline:** Daily stock data collection & analysis | Data collection started: Feb 4, 2026 \n
**Stocks Tracked:** NVDA, GOOG, AAPL, MSFT, AMZN, META, TSM, NFLX, TSLA, AVGO  \n
**Update Schedule:** Every day at 22:00 UTC (after US market close)
""")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "📈 Stock Analysis", "💼 Portfolio", "🔗 Correlations"])

# ============================================================================
# TAB 1: MARKET OVERVIEW
# ============================================================================
with tab1:
    st.header("Market Overview")
    
    # Get latest data
    latest_data = get_latest_stock_prices()
    
    if latest_data.empty:
        st.warning("No data available yet. Run the data collection script first!")
    else:
        # Display date
        latest_date = latest_data['date'].iloc[0]
        st.subheader(f"Data as of: {latest_date}")
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_return = latest_data['daily_return_percent'].mean()
            st.metric("Average Daily Return", f"{avg_return:.2f}%")
        
        with col2:
            best_stock = latest_data.loc[latest_data['daily_return_percent'].idxmax()]
            st.metric(
                "Best Performer", 
                best_stock['ticker'],
                f"+{best_stock['daily_return_percent']:.2f}%"
            )
        
        with col3:
            worst_stock = latest_data.loc[latest_data['daily_return_percent'].idxmin()]
            st.metric(
                "Worst Performer", 
                worst_stock['ticker'],
                f"{worst_stock['daily_return_percent']:.2f}%"
            )
        
        with col4:
            total_volume = latest_data['volume'].sum()
            st.metric("Total Volume", f"{total_volume:,.0f}")
        
        st.markdown("---")
        
        # Stock table
        st.subheader("All Stocks")
        
        # Format the dataframe for display
        display_df = latest_data[['ticker', 'company_name', 'close_price', 'volume', 
                                   'daily_return_percent', 'cumulative_return_percent']].copy()
        display_df.columns = ['Ticker', 'Company', 'Price ($)', 'Volume', 
                              'Daily Return (%)', 'Cumulative Return (%)']
        
        # Color-code returns
        st.dataframe(
            display_df.style.background_gradient(
                subset=['Daily Return (%)', 'Cumulative Return (%)'],
                cmap='RdYlGn',
                vmin=-5,
                vmax=5
            ).format({
                'Price ($)': '{:.2f}',
                'Volume': '{:,.0f}',
                'Daily Return (%)': '{:.2f}',
                'Cumulative Return (%)': '{:.2f}'
            }),
            use_container_width=True
        )
        
        # Bar chart of returns
        st.subheader("Daily Returns Comparison")
        fig = px.bar(
            latest_data,
            x='ticker',
            y='daily_return_percent',
            color='daily_return_percent',
            color_continuous_scale='RdYlGn',
            labels={'daily_return_percent': 'Return (%)', 'ticker': 'Stock'},
            title='Daily Returns by Stock'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# TAB 2: STOCK ANALYSIS
# ============================================================================
with tab2:
    st.header("Individual Stock Analysis")
    
    # Stock selector
    stock_info = get_stock_info()
    ticker = st.selectbox(
        "Select Stock",
        options=stock_info['ticker'].tolist(),
        format_func=lambda x: f"{x} - {stock_info[stock_info['ticker']==x]['company_name'].iloc[0]}"
    )
    
    # Get stock history
    history = get_stock_history(ticker, limit=30)
    
    if history.empty:
        st.warning(f"No historical data for {ticker}")
    else:
        # Stock info
        stock_details = stock_info[stock_info['ticker'] == ticker].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Company", stock_details['company_name'])
        with col2:
            st.metric("Sector", stock_details['sector'])
        with col3:
            market_cap_b = stock_details['market_cap'] / 1e9
            st.metric("Market Cap", f"${market_cap_b:.1f}B")
        
        st.markdown("---")
        
        # Candlestick chart
        st.subheader(f"{ticker} Price Chart (Last 30 Days)")
        
        fig = go.Figure(data=[go.Candlestick(
            x=history['date'],
            open=history['open_price'],
            high=history['high_price'],
            low=history['low_price'],
            close=history['close_price'],
            name=ticker
        )])
        
        fig.update_layout(
            title=f'{ticker} Stock Price',
            yaxis_title='Price ($)',
            xaxis_title='Date',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume chart
        st.subheader(f"{ticker} Trading Volume")
        
        fig_volume = px.bar(
            history,
            x='date',
            y='volume',
            title=f'{ticker} Trading Volume',
            labels={'volume': 'Volume', 'date': 'Date'}
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)

# ============================================================================
# TAB 3: PORTFOLIO PERFORMANCE
# ============================================================================
with tab3:
    st.header("Portfolio Performance")
    st.markdown("*Assumes $100 invested in each stock on Day 1*")
    
    portfolio_data = get_portfolio_performance()
    
    if portfolio_data.empty:
        st.warning("No portfolio data available yet")
    else:
        # Sort by date ascending for charts
        portfolio_data = portfolio_data.sort_values('date')
        
        # Current portfolio value
        current_value = portfolio_data['total_portfolio_value'].iloc[-1]
        initial_value = 1000  # $100 × 10 stocks
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Initial Investment", f"${initial_value:,.2f}")
        with col2:
            st.metric("Current Value", f"${current_value:,.2f}")
        with col3:
            st.metric("Total Return", f"{total_return:.2f}%", delta=f"{total_return:.2f}%")
        
        st.markdown("---")
        
        # Portfolio value over time
        st.subheader("Portfolio Value Over Time")
        
        fig = px.line(
            portfolio_data,
            x='date',
            y='total_portfolio_value',
            title='Portfolio Value Trend',
            labels={'total_portfolio_value': 'Portfolio Value ($)', 'date': 'Date'}
        )
        
        # Add initial investment line
        fig.add_hline(
            y=initial_value, 
            line_dash="dash", 
            line_color="gray",
            annotation_text="Initial Investment"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Best/Worst performers
        st.subheader("Best & Worst Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Best Performers**")
            best_counts = portfolio_data['best_performer'].value_counts().head(5)
            st.dataframe(best_counts.rename('Days as Best'), use_container_width=True)
        
        with col2:
            st.markdown("**Worst Performers**")
            worst_counts = portfolio_data['worst_performer'].value_counts().head(5)
            st.dataframe(worst_counts.rename('Days as Worst'), use_container_width=True)

# ============================================================================
# TAB 4: CORRELATIONS
# ============================================================================
with tab4:
    st.header("Stock Correlations")
    
    all_returns = get_all_returns()
    
    if all_returns.empty:
        st.warning("Not enough data for correlation analysis")
    else:
        # Pivot data for correlation
        pivot_data = all_returns.pivot(
            index='date',
            columns='ticker',
            values='daily_return_percent'
        )
        
        if len(pivot_data) < 2:
            st.warning("Need at least 2 days of data for correlation analysis")
        else:
            # Calculate correlation matrix
            corr_matrix = pivot_data.corr()
            
            st.subheader("Correlation Matrix")
            st.markdown("*Values closer to 1 mean stocks move together*")
            
            # Heatmap
            fig = px.imshow(
                corr_matrix,
                labels=dict(color="Correlation"),
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                color_continuous_scale='RdBu_r',
                zmin=-1,
                zmax=1,
                title='Stock Return Correlations'
            )
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Multi-stock comparison
            st.subheader("Compare Multiple Stocks")
            
            selected_stocks = st.multiselect(
                "Select stocks to compare (2-5)",
                options=pivot_data.columns.tolist(),
                default=pivot_data.columns.tolist()[:3]
            )
            
            if len(selected_stocks) >= 2:
                comparison_data = pivot_data[selected_stocks].reset_index()
                comparison_data = comparison_data.melt(
                    id_vars='date',
                    var_name='ticker',
                    value_name='return'
                )
                
                fig = px.line(
                    comparison_data,
                    x='date',
                    y='return',
                    color='ticker',
                    title='Daily Returns Comparison',
                    labels={'return': 'Daily Return (%)', 'date': 'Date'}
                )
                
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("*Data updated daily at 22:00 UTC via Apache Airflow*")