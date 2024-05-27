import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, sys
from firebase_admin import credentials, auth, db, exceptions
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db import get_user_investments, get_user_price_alerts, get_user_by_uid, update_user_price_alerts

def send_email_alert(uid, symbol, current_price, threshold_price):
    user = get_user_by_uid(uid)
    email = user.get('email')

    if not email:
        print(f"No email found for user {uid}")
        return

    sender_email = os.getenv("APP_EMAIL")
    sender_password = os.getenv("APP_PASS")

    subject = f"Stock Price Alert for {symbol}"
    body = f"The price of {symbol} has reached ${current_price}, which is above your threshold of ${threshold_price}."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email, msg.as_string())
        print(f"Email sent to {email}: {body}")
    except Exception as e:
        print(f"Error sending email: {e}")

def check_stock_prices(uid):
    user_investments = get_user_investments(uid)
    if not user_investments:
        print(f"No investments found for user with UID {uid}.")
        return
    
    try:
        auth.get_user(uid)
    except exceptions.FirebaseError:
        print(f"User with UID {uid} does not exist. Skipping...")
        return
    
    price_alerts = get_user_price_alerts(uid) or {}
    for symbol, thresholds in price_alerts.items():
        current_price = yf.Ticker(symbol).history(period='1d')['Close'].iloc[0]
        
        for alert_id, alert_data in thresholds.items():
            threshold_price = alert_data
            
            if current_price >= threshold_price:
                send_email_alert(uid, symbol, current_price, threshold_price)
                update_user_price_alerts(uid, symbol, threshold_price)

if __name__ == "__main__":
    check_stock_prices()
