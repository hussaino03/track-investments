import unittest
from unittest.mock import patch
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import stocks as api

class TestAPI(unittest.TestCase):

    @patch('api.stocks.requests.get')
    def test_get_stock_symbol(self, mock_get):
        mock_response = {
            "bestMatches": [
                {
                    "1. symbol": "TSLA",
                    "2. name": "Tesla Inc.",
                    "3. type": "Equity",
                    "4. region": "United States",
                    "5. marketOpen": "09:30",
                    "6. marketClose": "16:00",
                    "7. timezone": "UTC-05",
                    "8. currency": "USD",
                    "9. matchScore": "0.7273"
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        
        company_name = "Tesla"
        expected_symbol = "TSLA"
        
        symbol = api.get_stock_symbol(company_name)
        self.assertEqual(symbol, expected_symbol, f"Failed to fetch the correct symbol for {company_name}")

    @patch('api.stocks.requests.get')
    def test_get_stock_price(self, mock_get):
        mock_response = {
            "Time Series (1min)": {
                "2022-05-20 16:00:00": {
                    "1. open": "900.00",
                    "2. high": "905.00",
                    "3. low": "895.00",
                    "4. close": "902.50",
                    "5. volume": "3000"
                }
            }
        }
        mock_get.return_value.json.return_value = mock_response
        
        symbol = "TSLA"
        expected_price = 902.50
        
        price = api.get_stock_price(symbol)
        self.assertEqual(price, expected_price, f"Failed to fetch the correct price for {symbol}")

if __name__ == "__main__":
    unittest.main()