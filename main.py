import json
import datetime
import os
from parser import parser as p
from api import stocks as api
from firebase_admin import credentials, auth, db
from db.db import create_user, clear_user_price_alerts, get_user_investments, save_report_to_db, get_report_from_db, get_chart_from_db, save_chart_to_db
from graph.graph import plot_bar_chart, decode_base64_to_image, encode_image_to_base64
from alerts.alert import update_user_price_alerts, check_stock_prices

def analyze_portfolio(investments):
    """Analyze the user's portfolio to determine distribution by sector."""
    sector_distribution = {}
    for investment in investments:
        sector = api.get_sector(investment['ticker'])
        if sector:
            if sector in sector_distribution:
                sector_distribution[sector] += investment['total_value']
            else:
                sector_distribution[sector] = investment['total_value']
    return sector_distribution


def get_investment_recommendations(portfolio_stats):
    """Generate investment recommendations based on portfolio distribution and market trends."""
    recommendations = {}

    try:
        if isinstance(portfolio_stats, dict):
            most_invested_sector = max(portfolio_stats, key=portfolio_stats.get)
            recommendations["most_invested_sector"] = most_invested_sector

            top_stocks = api.get_stocks_per_sector(most_invested_sector)
            recommendations["top_stocks_for_this_sector"] = top_stocks
        else:
            raise ValueError("Incorrect parsing")
    except Exception as e:
        print(f"Error in generating investment recommendations: {e}")

    return recommendations


def main():
    investment_data, existing_data = [], []
    username = input("What's your name? ")
    is_returning_user = input("Are you a returning user? (y/n): ").lower()
    
    if is_returning_user == 'y':
        while True:
            email = input("Enter email: ")
            try:
                user = auth.get_user_by_email(email)
                uid = user.uid
                report = get_report_from_db(uid)
                if report:
                    print("User Investment Report:")
                    print(json.dumps(report, indent=4))

                    encoded_chart = get_chart_from_db(uid)

                    if isinstance(report, dict):
                        existing_data = report.get("investments", [])
                    else:
                        existing_data = []

                    if encoded_chart:
                        decode_base64_to_image(encoded_chart, 'graph/investment_distribution.png')
                        print("Investment distribution chart saved to graph/investment_distribution.png")
                    else:
                        print("No investment distribution chart found for this user.")
                else:
                    print("No report found for this user.")
                break
            except auth.UserNotFoundError:
                print("No user found with this email. Please try again.")
            except ValueError as e:
                print(e)
                print("Please enter a valid email address.")
    else:
        while True:
            email = input("Enter email: ")
            password = input("Enter password: ")
            try:
                uid = create_user(email, password)
                break
            except ValueError as e:
                print(e)
                print("Please enter a valid email and a password that is at least 6 characters long.")

    print(f"Hello {username}, let's add your investment details. You can type 'exit' or 'quit' to finish at any time.")
    investment_date = datetime.datetime.now().strftime('%Y-%m-%d')

    two_weeks_ago = (datetime.datetime.now() - datetime.timedelta(weeks=2)).strftime('%Y-%m-%d')

    while True:
        user_input = input("\nWhat did you invest in today? ")

        if user_input.lower() in ["exit", "quit"]:
            break

        investment_info = p.extract_investment_info(username, user_input)

        investment_data.append(investment_info)

        if len(existing_data) == 0:
            print(f"\nInvestment {len(investment_data)}:")
        else:
            print(f"\nInvestment {len(investment_data) + len(existing_data)}:")
        print(f"  Entities: {investment_info['entities']}")
        print(f"  Amount: {investment_info['amount']}")
    
    subscribe_to_alerts = input("Do you want to subscribe to stock alerts for your investments? (y/n): ").lower()
    skip_all = False
    alerts_set = False

    data = []
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
                                "type": "stock",  
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
                            data.append(investment_entry)

                            if subscribe_to_alerts == 'y' and not skip_all:
                                while True:
                                    set_alert = input(f"Do you want to set up a price alert for {symbol}? (y/n/s to skip all): ").lower()
                                    if set_alert in ['y', 'n', 's']:
                                        break
                                    print("Invalid input. Please enter 'y' for yes, 'n' for no, or 's' to skip all.")

                                if set_alert == 'y':
                                    threshold_price = float(input(f"Enter the price threshold for {symbol}: "))
                                    update_user_price_alerts(uid, symbol, threshold_price)
                                    alerts_set = True
                                elif set_alert == 's':
                                    print("Skipping price alert setup for all remaining investments.")
                                    skip_all = True
                        else:
                            print(f"Could not fetch the price for {entity[0]} ({symbol})")
                else:
                    print(f"Could not find stock symbol for {entity[0]}")

    if subscribe_to_alerts != 'y':
        clear_user_price_alerts(uid)
        print("Any existing price alerts have been cleared")
    
    if len(existing_data) != 0:
        investment_data = existing_data + data
    else:
        investment_data = data

    user_report = {
        "username": username,
        "investments": investment_data,
        "stock_alerts": "on" if alerts_set else "off"
    }

    portfolio_distribution = analyze_portfolio(investment_data)
    recommendations = get_investment_recommendations(portfolio_distribution)

    stats_report = {
        "distribution": portfolio_distribution,
        "recommendations": recommendations
    }

    user_report["Stats"] = stats_report

    file_name = f"{username}_investment_report.json"

    print(f"\nUser Investment Report has been saved to {file_name}")

    bar_chart_path = 'graph/investment_distribution.png'
    plot_bar_chart(user_report["investments"], bar_chart_path)
    encoded_chart = encode_image_to_base64(bar_chart_path)

    user_report_json = json.dumps(user_report, indent=4)

    with open(file_name, "w") as file:
        file.write(user_report_json)

    print(user_report)
    save_report_to_db(uid, user_report)
    save_chart_to_db(uid, encoded_chart)

    check_stock_prices(uid)

if __name__ == "__main__":
    main()
