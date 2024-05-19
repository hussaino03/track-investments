import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phase1 import parser as p
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
        
        for i, (user_name, user_input) in enumerate(test_cases):
            result = p.extract_investment_info(user_name, user_input)
            print(result)
            self.assertIsNotNone(result, f"Test Case {i+1}: {user_input} failed")

if __name__ == "__main__":
    unittest.main()
