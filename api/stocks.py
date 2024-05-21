import requests
import os

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_SEARCH_URL = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'
ALPHA_VANTAGE_PRICE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'
ALPHA_VANTAGE_DAILY_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY'
ALPHA_VANTAGE_OVERVIEW_URL = 'https://www.alphavantage.co/query?function=OVERVIEW'

def get_stock_symbol(company_name):
    """Fetch the stock symbol for a given company name using Alpha Vantage."""
    if company_name.lower() == "google":
        company_name = "Alphabet"
    url = f"{ALPHA_VANTAGE_SEARCH_URL}&keywords={company_name}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'bestMatches' in data and len(data['bestMatches']) > 0:
        return data['bestMatches'][0]['1. symbol']
    else:
        print(f"No symbol found for company: {company_name}")
        return None

def get_stock_price(symbol):
    """Fetch the current price of the stock with the given symbol using Alpha Vantage."""
    url = f"{ALPHA_VANTAGE_PRICE_URL}&symbol={symbol}&interval=1min&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (1min)' in data:
        latest_timestamp = max(data['Time Series (1min)'].keys())
        return float(data['Time Series (1min)'][latest_timestamp]['4. close'])
    else:
        print(f"Error fetching stock price for {symbol}: {data}")
        return None

def get_initial_stock_price(symbol, date):
    """Fetch the stock price for a given symbol on a specific date using Alpha Vantage."""
    url = f"{ALPHA_VANTAGE_DAILY_URL}&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        if date in data['Time Series (Daily)']:
            return float(data['Time Series (Daily)'][date]['4. close'])
        else:
            print(f"No data available for {symbol} on {date}")
            return None
    else:
        print(f"Error fetching initial stock price for {symbol}: {data}")
        return None

def get_market_cap(symbol):
    """Fetch the market capitalization of the stock with the given symbol using Alpha Vantage."""
    url = f"{ALPHA_VANTAGE_OVERVIEW_URL}&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'MarketCapitalization' in data:
        return float(data['MarketCapitalization'])
    else:
        print(f"Error fetching market capitalization for {symbol}: {data}")
        return None

def format_market_cap(market_cap):
    """Format the market capitalization value for readability."""
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
