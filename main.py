import json
import datetime
from parser import parser as p
from api import stocks as api
from firebase_admin import credentials, auth, db
from db.db import create_user, add_investment_to_user, get_user_investments, save_report_to_db, get_report_from_db

def main():
    is_returning_user = input("Are you a returning user? (y/n): ").lower()
    if is_returning_user == 'y':
        email = input("Enter email: ")
        try:
            user = auth.get_user_by_email(email)
            uid = user.uid
            report = get_report_from_db(uid)
            if report:
                print("User Investment Report:")
                print(json.dumps(report, indent=4))
            else:
                print("No report found for this user.")
        except auth.UserNotFoundError:
            print("No user found with this email. Please register as a new user.")
            return
    else:
        email = input("Enter email: ")
        password = input("Enter password: ")

        uid = create_user(email, password)

        if not uid:
            print("Could not create user. Exiting.")
            return

    username = input("What's your name? ")
    investment_data = []

    print(f"Hello {username}, let's add your investment details. You can type 'exit' or 'quit' to finish at any time.")

    while True:
        user_input = input("\nWhat did you invest in today? ")

        if user_input.lower() in ["exit", "quit"]:
            break

        investment_info = p.extract_investment_info(username, user_input)

        investment_data.append(investment_info)

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
                        market_cap = api.get_market_cap(symbol)
                        if current_price:
                            number_of_shares = amount / current_price
                            total_value = current_price * number_of_shares
                            gain_loss = total_value - amount
                            percentage_change = (gain_loss / amount) * 100
                            formatted_market_cap = api.format_market_cap(market_cap) if market_cap else "N/A"
                            investment_date = datetime.datetime.now().strftime('%Y-%m-%d')

                            investment_entry = {
                                "type": "stock",  # assuming all are stocks for simplicity
                                "amount": {"$numberInt": str(int(amount))},
                                "ticker": entity[0],
                                "investment_date": investment_date,
                                "current_price": current_price,
                                "number_of_shares": number_of_shares,
                                "total_value": total_value,
                                "market_cap": formatted_market_cap
                            }
                            user_report["investments"].append(investment_entry)
                        else:
                            print(f"Could not fetch the price for {entity[0]} ({symbol})")
                else:
                    print(f"Could not find stock symbol for {entity[0]}")

    user_report_json = json.dumps(user_report, indent=4)

    file_name = f"{username}_investment_report.json"

    with open(file_name, "w") as file:
        file.write(user_report_json)

    print(f"\nUser Investment Report has been saved to {file_name}")

    save_report_to_db(uid, user_report)

if __name__ == "__main__":
    main()
