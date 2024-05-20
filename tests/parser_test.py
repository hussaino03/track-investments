import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase1 import parser
import unittest

class TestParser(unittest.TestCase):
    def test_extraction(self):
        test_cases = [
            ("John Doe", "invested $500 in Tesla"),
            ("Jane Doe", "yo whatsup I just invested 5 bands into Tesla right now"),
            ("Alice", "I just put $1200 into Apple stocks"),
            ("Bob", "Added 2000 dollars to Microsoft investment"),
            ("Charlie", "Just dropped $300 on Amazon shares")
        ]
        
        expected_results = [
            {'entities': [('Tesla', 'ORG')], 'amount': [500.0], 'username': 'John Doe'},
            {'entities': [('Tesla', 'ORG')], 'amount': [5.0], 'username': 'Jane Doe'},
            {'entities': [('Apple', 'ORG')], 'amount': [1200.0], 'username': 'Alice'},
            {'entities': [('Microsoft', 'ORG')], 'amount': [2000.0], 'username': 'Bob'},
            {'entities': [('Amazon', 'ORG')], 'amount': [300.0], 'username': 'Charlie'}
        ]
        
        for i, (user_name, user_input) in enumerate(test_cases):
            result = parser.extract_investment_info(user_name, user_input)
            print(result)
            self.assertEqual(result['entities'], expected_results[i]['entities'], f"Test Case {i+1}: {user_input} failed")
            self.assertEqual(result['amount'], expected_results[i]['amount'], f"Test Case {i+1}: {user_input} failed")

if __name__ == "__main__":
    unittest.main()
