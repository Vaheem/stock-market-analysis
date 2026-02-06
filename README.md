# Tech Stock Market Analytics

An automated data engineering pipeline that tracks the top tech stocks, performs financial analytics, and visualizes market trends through an interactive dashboard.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

---

## Project Overview

This project demonstrates a **production-ready data engineering pipeline** that:
- Automatically collects daily stock market data from Alpha Vantage API
- Stores OHLC (Open, High, Low, Close) data in PostgreSQL
- Calculates financial metrics (daily returns, cumulative returns, portfolio performance)
- Orchestrates workflows with Apache Airflow
- Visualizes data through an interactive Streamlit dashboard

**Data Collection Started:** February 4, 2026

---

## Architecture
```
Alpha Vantage API
      ↓
Python ETL Script (Daily at 22:00 UTC)
      ↓
PostgreSQL Database
      ↓
Analytics Engine (Calculate Returns & Portfolio)
      ↓
Streamlit Dashboard (Real-time Visualization)
      
All orchestrated by Apache Airflow
```

---

## Features

### Data Pipeline
- **Automated Data Collection**: Fetches stock prices daily after US market close
- **Error Handling**: Retry logic for API failures and rate limiting
- **Data Quality**: Prevents duplicates, validates data integrity

### Analytics
- **Daily Returns**: Percentage change calculations
- **Cumulative Returns**: Total return since start date
- **Portfolio Performance**: Tracks $100 investment per stock
- **Best/Worst Performers**: Daily winners and losers

### Dashboard
- **Market Overview**: Key metrics and performance summary
- **Stock Analysis**: Individual stock charts (Candlestick, Volume)
- **Portfolio Tracking**: Portfolio value over time
- **Correlation Analysis**: Stock relationship heatmap

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **Data Source** | Alpha Vantage API |
| **Database** | PostgreSQL 15 |
| **Orchestration** | Apache Airflow 2.7.1 |
| **Data Processing** | Python 3.9, Pandas |
| **Visualization** | Streamlit, Plotly |
| **Containerization** | Docker, Docker Compose |

---

## Stocks Tracked

| Ticker | Company | Sector |
|--------|---------|--------|
| NVDA | NVIDIA Corporation | Technology |
| GOOG | Alphabet Inc. | Technology |
| AAPL | Apple Inc. | Technology |
| MSFT | Microsoft Corporation | Technology |
| AMZN | Amazon.com Inc. | Consumer Cyclical |
| META | Meta Platforms Inc. | Technology |
| TSM | Taiwan Semiconductor | Technology |
| NFLX | Netflix Inc. | Communication Services |
| TSLA | Tesla Inc. | Automotive |
| AVGO | Broadcom Inc. | Technology |

---

## Installation & Setup

### Prerequisites
- Docker Desktop installed
- Alpha Vantage API key ([Get free key](https://www.alphavantage.co/support/#api-key))

### Quick Start

1. **Clone the repository**
```bash
   git clone https://github.com/YOUR_USERNAME/stock-market-analysis.git
   cd stock-market-analysis
```

2. **Create environment file**
```bash
   cp .env.example .env
```

3. **Configure your `.env` file**
```env
   POSTGRES_PASSWORD=your_strong_password
   AIRFLOW_PASSWORD=your_strong_password
   ALPHA_VANTAGE_API_KEY=your_api_key
```

4. **Start the application**
```bash
   docker-compose up -d
```

5. **Create Airflow admin user**
```bash
   docker exec -it airflow_webserver airflow users create \
     --username admin \
     --firstname Admin \
     --lastname User \
     --role Admin \
     --email admin@example.com \
     --password YOUR_PASSWORD
```

6. **Access the applications**
   - Airflow UI: http://localhost:8080
   - Streamlit Dashboard: http://localhost:8501

---

## Database Schema

### `stock_prices` (Fact Table)
Daily OHLC data for each stock

### `stock_info` (Dimension Table)
Company information and market cap

### `daily_returns` (Analytics)
Calculated percentage returns

### `portfolio_performance` (Aggregated)
Overall portfolio metrics

---

## Workflow

1. **Daily Execution** (22:00 UTC)
   - Airflow triggers data collection DAG
   - Python script fetches latest stock prices
   - Data validated and stored in PostgreSQL

2. **Analytics Processing**
   - Calculate daily returns for each stock
   - Calculate cumulative returns
   - Update portfolio performance
   - Identify best/worst performers

3. **Visualization**
   - Streamlit dashboard reads from database
   - Charts update with latest data
   - Users can explore trends and correlations

---

## Dashboard Features

### Market Overview Tab
- Average daily return across all stocks
- Best and worst performing stocks
- Total trading volume
- Color-coded performance table

### Stock Analysis Tab
- Candlestick charts for price visualization
- Volume analysis
- Company information and market cap

### Portfolio Tab
- Portfolio value over time
- Return on investment
- Historical best/worst performers

### Correlations Tab
- Heatmap showing stock correlations
- Multi-stock comparison charts

---

## License

This project is open source and available under the MIT License.

---

## Author

**Your Name**
- GitHub: [@Vaheem](https://github.com/Vaheem)
- LinkedIn: [vahe-eminyan](https://www.linkedin.com/in/vahe-eminyan-3719782a3/)

---

## Acknowledgments

- Data provided by [Alpha Vantage](https://www.alphavantage.co/)
- Built with [Apache Airflow](https://airflow.apache.org/)
- Visualized with [Streamlit](https://streamlit.io/)

---

**If you find this project useful, please consider giving it a star!**