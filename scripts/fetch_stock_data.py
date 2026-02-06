import os
import requests
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

# Load environment variables
load_dotenv()

# API Configuration
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'), 
    'port': os.getenv('POSTGRES_PORT', '5432')   # Port ist OK als Fallback
}

# Stock Tickers
TICKERS = ['NVDA', 'GOOG', 'AAPL', 'MSFT', 'AMZN', 
           'META', 'TSM', 'NFLX', 'TSLA', 'AVGO']

def fetch_stock_data(ticker):
    """
    Fetch daily stock data for a given ticker(Company's short name) from Alpha Vantage API
    Returns: dict with OHLC data or None if error
    """

    # Prepare the API parameters
    # https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=API_KEY
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': API_KEY
    }
    
    try:
        print(f"Fetching data for {ticker}...")
        # Concatenates BASE_URL and params
        response = requests.get(BASE_URL, params=params)
        # Transform JSON into python dict
        data = response.json()
        
        # Check for errors
        if 'Error Message' in data:
            print(f"Error: Invalid ticker {ticker}")
            return None
        
        if 'Note' in data:
            print(f"API limit reached!")
            return None
        
        # Get latest date data: a dictinary of the format date: OHLC, that contains many days 
        time_series = data.get('Time Series (Daily)', {})
        if not time_series:
            print(f"No data found for {ticker}")
            return None
        
        # Get most recent date, and the corresponding OHLC data
        # Data of the current day
        latest_date = list(time_series.keys())[0]
        latest_data = time_series[latest_date]
        
        # Returns a dictonary of the company values of the current day
        return {
            'ticker': ticker,
            'date': latest_date,
            'open': float(latest_data['1. open']),
            'high': float(latest_data['2. high']),
            'low': float(latest_data['3. low']),
            'close': float(latest_data['4. close']),
            'volume': int(latest_data['5. volume'])
        }
        
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None
    

def save_to_database(stock_data):
    """
    Save stock data to PostgreSQL database
    """
    if not stock_data:
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Insert data
        cursor.execute("""
            INSERT INTO stock_prices (ticker, date, open_price, high_price, low_price, close_price, volume, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (ticker, date) DO NOTHING
        """, (
            stock_data['ticker'],
            stock_data['date'],
            stock_data['open'],
            stock_data['high'],
            stock_data['low'],
            stock_data['close'],
            stock_data['volume']
        ))
        
        conn.commit()
        print(f"Done: Saved {stock_data['ticker']} data to database")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error saving to database: {e}")
        return False


def main():
    """
    Main function to fetch and save stock data for all tickers
    """
    print("=" * 50)
    print("Starting Stock Data Collection")
    print("=" * 50)
    
    # Check if API key is set
    if not API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY not found in environment variables!")
        return
    
    success_count = 0
    fail_count = 0
    
    # Loop through all tickers
    for ticker in TICKERS:
        print(f"\nProcessing {ticker}...")
        
        # Fetch data from API
        stock_data = fetch_stock_data(ticker)
        
        if stock_data:
            # Save to database
            if save_to_database(stock_data):
                success_count += 1
            else:
                fail_count += 1
        else:
            fail_count += 1
        
        # Rate limiting: wait 12 seconds between requests (5 calls per minute max)
        import time
        if ticker != TICKERS[-1]:  # Don't wait after last ticker
            print("Waiting 12 seconds (API rate limit)...")
            time.sleep(12)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Data Collection Complete!")
    print(f"Success: {success_count}/{len(TICKERS)}")
    print(f"Failed: {fail_count}/{len(TICKERS)}")
    print("=" * 50)


# Run the script
if __name__ == "__main__":
    main()