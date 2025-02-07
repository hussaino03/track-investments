import requests
import yfinance as yf
from datetime import datetime, timedelta
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_ticker(company_name):
    """Fetch information about a company using Yahoo Finance search."""
    yfinance_url = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    try:
        response = requests.get(url=yfinance_url, params=params, headers={'User-Agent': user_agent})
        data = response.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes'][0]['symbol']
        else:
            print(f"No information found for company: {company_name}")
            return None
    except Exception as e:
        print(f"Error fetching data for company: {company_name}: {e}")
        return None

def get_stock_price(symbol):
    """Fetch the current price of the stock with the given symbol using Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        todays_data = stock.history(period='1d')
        if not todays_data.empty:
            return todays_data['Close'].iloc[0]
        else:
            print(f"Error fetching stock price for {symbol}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching stock price for {symbol}: {e}")
        return None

def get_initial_stock_price(symbol, start_date, end_date):
    """Fetch the initial stock price for a given symbol within a specific date range."""
    try:
        stock = yf.Ticker(symbol)
        historical_data = stock.history(start=start_date, end=end_date)
        if not historical_data.empty:
            return historical_data['Close'].iloc[0]  
        else:
            print(f"No data available for {symbol} within the specified date range.")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching initial stock price for {symbol}: {e}")
        return None

def get_market_cap(symbol):
    """Fetch the market capitalization of the stock with the given symbol using Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        market_cap = stock.info.get('marketCap')
        if market_cap:
            return market_cap
        else:
            print(f"Error fetching market capitalization for {symbol}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching market capitalization for {symbol}: {e}")
        return None

def format_market_cap(market_cap):
    """Format the market capitalization value for readability."""
    if market_cap is None:
        return "N/A"
    
    trillion = 1e12
    billion = 1e9
    million = 1e6

    if market_cap >= trillion:
        return f"{market_cap / trillion:.2f} trillion"
    elif market_cap >= billion:
        return f"{market_cap / billion:.2f} billion"
    elif market_cap >= million:
        return f"{market_cap / million:.2f} million"
    else:
        return str(market_cap)

def get_sector(symbol):
    """Fetch the sector of a company using Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        sector = stock.info.get('sector')
        return sector
    except Exception as e:
        print(f"Exception occurred while fetching sector for {symbol}: {e}")
        return None

def get_stocks_per_sector(sector, num_stocks=5):
    """Fetch the current price of stocks within a given sector."""
    api_key = os.getenv("FINANCE_MODELLING")
    url = f"https://financialmodelingprep.com/api/v3/stock-screener?sector={sector}&limit={num_stocks}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    stock_prices = {}
    for company in data:
        symbol = company['symbol']
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            stock_prices[symbol] = current_price

    sorted_stocks = sorted(stock_prices.items(), key=lambda x: x[1], reverse=True)
    return sorted_stocks[:num_stocks]
