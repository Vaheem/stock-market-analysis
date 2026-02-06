import os
import psycopg2
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}


def get_connection():
    """
    Create database connection
    """
    return psycopg2.connect(**DB_CONFIG)


def get_latest_stock_prices():
    """
    Get the most recent stock prices for all tickers
    Returns: pandas DataFrame
    """
    query = """
        SELECT 
            sp.ticker,
            si.company_name,
            sp.date,
            sp.close_price,
            sp.volume,
            dr.daily_return_percent,
            dr.cumulative_return_percent
        FROM stock_prices sp
        JOIN stock_info si ON sp.ticker = si.ticker
        LEFT JOIN daily_returns dr ON sp.ticker = dr.ticker AND sp.date = dr.date
        WHERE sp.date = (SELECT MAX(date) FROM stock_prices)
        ORDER BY sp.ticker
    """
    
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_stock_history(ticker, limit=30):
    """
    Get historical prices for a specific ticker
    Returns: pandas DataFrame
    """
    query = """
        SELECT 
            date,
            open_price,
            high_price,
            low_price,
            close_price,
            volume
        FROM stock_prices
        WHERE ticker = %s
        ORDER BY date DESC
        LIMIT %s
    """
    
    conn = get_connection()
    df = pd.read_sql(query, conn, params=(ticker, limit))
    conn.close()
    
    # Sort by date ascending for charts
    df = df.sort_values('date')
    return df


def get_all_returns():
    """
    Get daily returns for all stocks
    Returns: pandas DataFrame
    """
    query = """
        SELECT 
            dr.ticker,
            si.company_name,
            dr.date,
            dr.daily_return_percent,
            dr.cumulative_return_percent
        FROM daily_returns dr
        JOIN stock_info si ON dr.ticker = si.ticker
        ORDER BY dr.date DESC, dr.ticker
    """
    
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_portfolio_performance():
    """
    Get portfolio performance history
    Returns: pandas DataFrame
    """
    query = """
        SELECT 
            date,
            total_portfolio_value,
            best_performer,
            worst_performer,
            daily_return_percent
        FROM portfolio_performance
        ORDER BY date DESC
    """
    
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


def get_stock_info():
    """
    Get all stock information
    Returns: pandas DataFrame
    """
    query = """
        SELECT 
            ticker,
            company_name,
            sector,
            market_cap
        FROM stock_info
        ORDER BY ticker
    """
    
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df