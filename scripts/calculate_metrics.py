import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST'),
    'database': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# Stock Tickers
TICKERS = ['NVDA', 'GOOG', 'AAPL', 'MSFT', 'AMZN', 
           'META', 'TSM', 'NFLX', 'TSLA', 'AVGO']


def calculate_daily_returns():
    """
    Calculate daily and cumulative returns for each stock
    Daily Return = ((Close Today - Close Yesterday) / Close Yesterday) * 100
    Cumulative Return = ((Close Today - Close First Day) / Close First Day) * 100
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        for ticker in TICKERS:

            # Get all prices sorted newest → oldest
            cursor.execute("""
                SELECT date, close_price
                FROM stock_prices
                WHERE ticker = %s
                ORDER BY date DESC
            """, (ticker,))
            rows = cursor.fetchall()

            if not rows:
                continue

            today_date, today_price = rows[0]

            # Case 1: Only one day exists
            if len(rows) == 1:
                daily = 0
                cumulative = 0

            # Case 2: Normal case
            else:
                yesterday_price = rows[1][1]
                first_price = rows[-1][1]

                daily = (today_price - yesterday_price) / yesterday_price * 100
                cumulative = (today_price - first_price) / first_price * 100

            # Insert or update
            cursor.execute("""
                INSERT INTO daily_returns (ticker, date, daily_return_percent, cumulative_return_percent)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (ticker, date)
                DO UPDATE SET
                    daily_return_percent = EXCLUDED.daily_return_percent,
                    cumulative_return_percent = EXCLUDED.cumulative_return_percent
            """, (ticker, today_date, daily, cumulative))

        conn.commit()
        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print("Error:", e)
        return False


def calculate_portfolio_performance():
    """
    Calculate overall portfolio performance
    Assumes $100 invested in each stock on the first day
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get the most recent date
        cursor.execute("""
            SELECT MAX(date) FROM stock_prices
        """)
        latest_date = cursor.fetchone()[0]
        
        if not latest_date:
            print("No stock data found")
            return False
        
        # Get all tickers' performance for latest date
        cursor.execute("""
            SELECT ticker, cumulative_return_percent
            FROM daily_returns
            WHERE date = %s
        """, (latest_date,))
        returns = cursor.fetchall()
        
        if not returns:
            print(f"No returns calculated for {latest_date}")
            return False
        
        # Calculate portfolio value
        # Start: $100 per stock × 10 stocks = $1000
        initial_investment = 100 * len(TICKERS)
        total_value = 0
        
        best_performer = None
        worst_performer = None
        best_return = float('-inf')
        worst_return = float('inf')
        
        for ticker, cum_return in returns:
            # Calculate current value of this position
            position_value = 100 * (1 + cum_return / 100)
            total_value += position_value
            
            # Track best/worst
            if cum_return > best_return:
                best_return = cum_return
                best_performer = ticker
            
            if cum_return < worst_return:
                worst_return = cum_return
                worst_performer = ticker
        
        # Calculate overall portfolio return
        portfolio_return = ((total_value - initial_investment) / initial_investment) * 100
        
        # Insert into database
        cursor.execute("""
            INSERT INTO portfolio_performance 
            (date, total_portfolio_value, best_performer, worst_performer, daily_return_percent)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (date) 
            DO UPDATE SET
                total_portfolio_value = EXCLUDED.total_portfolio_value,
                best_performer = EXCLUDED.best_performer,
                worst_performer = EXCLUDED.worst_performer,
                daily_return_percent = EXCLUDED.daily_return_percent
        """, (latest_date, total_value, best_performer, worst_performer, portfolio_return))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"  Portfolio calculated for {latest_date}")
        print(f"  Total Value: ${total_value:.2f} (Return: {portfolio_return:.2f}%)")
        print(f"  Best: {best_performer} ({best_return:.2f}%)")
        print(f"  Worst: {worst_performer} ({worst_return:.2f}%)")
        
        return True
        
    except Exception as e:
        print(f"Error calculating portfolio: {e}")
        return False
    

def main():
    """
    Main function to calculate all analytics
    """
    print("=" * 50)
    print("Starting Analytics Calculation")
    print("=" * 50)
    
    # Step 1: Calculate daily returns for all stocks
    print("\n[1/2] Calculating daily returns...")
    if calculate_daily_returns():
        print("  Daily returns completed")
    else:
        print("  Daily returns failed")
        return
    
    # Step 2: Calculate portfolio performance
    print("\n[2/2] Calculating portfolio performance...")
    if calculate_portfolio_performance():
        print("  Portfolio performance completed")
    else:
        print("  Portfolio performance failed")
        return
    
    print("\n" + "=" * 50)
    print("Analytics Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()