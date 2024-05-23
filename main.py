import json
import datetime
import os
from parser import parser as p
from api import stocks as api
from firebase_admin import credentials, auth, db
from db.db import create_user, add_investment_to_user, get_user_investments, save_report_to_db, get_report_from_db
from graph.graph import plot_bar_chart

def main():
    username = input("What's your name? ")
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

    investment_data = []

    print(f"Hello {username}, let's add your investment details. You can type 'exit' or 'quit' to finish at any time.")
    investment_date = datetime.datetime.now().strftime('%Y-%m-%d')

    two_weeks_ago = (datetime.datetime.now() - datetime.timedelta(weeks=2)).strftime('%Y-%m-%d')

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
                symbol = api.get_ticker(entity[0])
                if symbol:
                    for amount in investment["amount"]:
                        initial_price = api.get_initial_stock_price(symbol, two_weeks_ago, investment_date)
                        current_price = api.get_stock_price(symbol)
                        market_cap = api.get_market_cap(symbol)
                        if current_price:
                            number_of_shares = amount / current_price
                            total_value = current_price * number_of_shares
                            initial_value = initial_price * number_of_shares
                            gain_loss = round((total_value - initial_value), 2)
                            percentage_change = round(((gain_loss / amount) * 100), 2)
                            formatted_market_cap = api.format_market_cap(market_cap) if market_cap else "N/A"

                            investment_entry = {
                                "type": "stock",  # assuming all are stocks for now
                                "amount": {"int": str(int(amount))},
                                "name": entity[0],
                                "ticker": symbol,
                                "investment_date": investment_date,
                                "initial_price": initial_price,
                                "current_price": current_price,
                                "number_of_shares": number_of_shares,
                                "initial_value": initial_value,
                                "total_value": total_value,
                                "gain_loss": gain_loss,
                                "percentage_change": percentage_change,
                                "market_cap": formatted_market_cap
                            }
                            user_report["investments"].append(investment_entry)
                        else:
                            print(f"Could not fetch the price for {entity[0]} ({symbol})")
                else:
                    print(f"Could not find stock symbol for {entity[0]}")

    file_name = f"{username}_investment_report.json"

    print(f"\nUser Investment Report has been saved to {file_name}")

    # Plot both charts and save them
    bar_chart_path = 'graph/investment_distribution.png'
    plot_bar_chart(user_report["investments"], bar_chart_path)

    user_report["investments_distribution"] = os.path.relpath(bar_chart_path)

    user_report_json = json.dumps(user_report, indent=4)

    with open(file_name, "w") as file:
        file.write(user_report_json)

    print(user_report)
    save_report_to_db(uid, user_report)

if __name__ == "__main__":
    main()
