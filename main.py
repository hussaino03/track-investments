import json
from parser import parser as p
from api import stocks as api

def main():
    username = input("What's your name? ")
    investment_data = []

    print(f"Hello {username}, let's add your investment details. You can type 'exit' or 'quit' to finish at any time.")

    while True:
        user_input = input("\nWhat did you invest in today? ")

        if user_input.lower() in ["exit", "quit"]:
            break

        # Call the function and store its return value
        investment_info = p.extract_investment_info(username, user_input)

        # Append the returned information to the investment_data list
        investment_data.append(investment_info)

        # Print the processed investment data
        print(f"\nInvestment {len(investment_data)}:")
        print(f"  Entities: {investment_info['entities']}")
        print(f"  Amount: {investment_info['amount']}")

    # Create the mock user report
    user_report = {
        "username": username,
        "investments": []
    }

    for investment in investment_data:
        for entity in investment["entities"]:
            if entity[1] == "ORG":
                symbol = api.get_stock_symbol(entity[0])
                if symbol:
                    for amount in investment["amount"]:
                        current_price = api.get_stock_price(symbol)
                        if current_price:
                            number_of_shares = amount / current_price
                            investment_entry = {
                                "type": "stock",  # assuming all are stocks for simplicity
                                "amount": {"$numberInt": str(int(amount))},
                                "notes": entity[0],
                                "current_price": current_price,
                                "number_of_shares": number_of_shares
                            }
                            user_report["investments"].append(investment_entry)
                        else:
                            print(f"Could not fetch the price for {entity[0]} ({symbol})")
                else:
                    print(f"Could not find stock symbol for {entity[0]}")

    # Convert the user report to JSON
    user_report_json = json.dumps(user_report, indent=4)

    # Define the file name
    file_name = f"{username}_investment_report.json"

    # Save the JSON report to a file
    with open(file_name, "w") as file:
        file.write(user_report_json)

    print(f"\nUser Investment Report has been saved to {file_name}")

# Call the main function
if __name__ == "__main__":
    main()
