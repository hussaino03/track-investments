import unittest
from unittest.mock import patch, MagicMock
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api import stocks as api

class TestAPI(unittest.TestCase):

    @patch('api.stocks.requests.get')
    def test_get_stock_symbol(self, mock_get):
        mock_response = {
            "quotes": [
                {
                    "symbol": "TSLA",
                    "longname": "Tesla Inc.",
                }
            ]
        }
        mock_get.return_value.json.return_value = mock_response
        
        company_name = "Tesla"
        expected_symbol = "TSLA"
        
        symbol = api.get_ticker(company_name)
        self.assertEqual(symbol, expected_symbol, f"Failed to fetch the correct symbol for {company_name}")

    @patch('api.stocks.yf.Ticker')
    def test_get_stock_price(self, mock_ticker):
        # Mock the return value for the `history` method
        mock_ticker_instance = mock_ticker.return_value
        mock_data = MagicMock()
        mock_data.empty = False
        mock_data.__getitem__.return_value = [902.50]
        mock_ticker_instance.history.return_value = mock_data
        
        symbol = "TSLA"
        expected_price = 902.50
        
        price = api.get_stock_price(symbol)
        self.assertEqual(price, expected_price, f"Failed to fetch the correct price for {symbol}")

if __name__ == "__main__":
    unittest.main()
