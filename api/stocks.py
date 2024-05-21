import requests
import os

api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_SEARCH_URL = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH'
ALPHA_VANTAGE_PRICE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY'

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

