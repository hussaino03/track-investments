from phase1 import parser as p

def main():
    username = input("What's your name? ")
    user_input = input(f"Hi {username}! What did you invest in today? ")

    # Call the function and store its return value
    investment_info = p.extract_investment_info(username, user_input)

    # Print the returned information
    print(f"User: {investment_info['username']}")
    print(f"Investment Entities: {investment_info['entities']}")
    print(f"Investment Amount: {investment_info['amount']}")

# Call the main function
if __name__ == "__main__":
    main()
