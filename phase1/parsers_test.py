import parsers as p

def test_extraction():
    test_cases = [
        "invested $500 in Tesla",
        "yo whatsup I just invested 5 bands into Tesla right now",
        "I just put $1200 into Apple stocks",
        "Added 2000 dollars to Microsoft investment",
        "Just dropped $300 on Amazon shares"
    ]
    
    for i, user_input in enumerate(test_cases):
        result = p.extract_investment_info(user_input)
        print(f"Test Case {i+1}: {user_input}\nParsed Output: {result}\n")

if __name__ == "__main__":
    test_extraction()