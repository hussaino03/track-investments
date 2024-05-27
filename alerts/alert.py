import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, sys
from firebase_admin import credentials, auth, db, exceptions
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from email.mime.base import MIMEBase
from email import encoders
from db.db import get_report_from_db, update_user_price_alerts

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.db import get_user_investments, get_user_price_alerts, get_user_by_uid

def generate_pdf_report(report, filename):
    username = report.get("username", "Unknown User")
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph(f"{username} Investment Report", styles['Title'])
    elements.append(title)
    
    elements.append(Paragraph("<br/>", styles['Normal']))
    
    stats = report.get("Stats", {})
    if stats:
        elements.append(Paragraph("Stats:", styles['Heading2']))
        
        distribution = stats.get("distribution", {})
        recommendations = stats.get("recommendations", {})

        table_data = [["Metric", "Value"]]
        for key, value in distribution.items():
            table_data.append([f"Distribution: {key}", value])

        for key, value in recommendations.items():
            if key == "top_stocks_for_this_sector":
                value = ', '.join([f"{stock[0]}: ${stock[1]:.2f}" for stock in value])
            table_data.append([f"Recommendations: {key}", value])
        
        stats_table = Table(table_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Paragraph("<br/>", styles['Normal']))

    investments = report.get("investments", [])
    if investments:
        elements.append(Paragraph("Investments:", styles['Heading2']))
        
        table_data = [["Name", "Ticker", "Amount", "Current Price", "Initial Price", "Gain/Loss", "Percentage Change", "Total Value"]]
        for investment in investments:
            amount = investment.get("amount", {}).get("int", "0")
            row = [
                investment.get("name", ""),
                investment.get("ticker", ""),
                amount,
                f"${investment.get('current_price', 0):.2f}",
                f"${investment.get('initial_price', 0):.2f}",
                f"${investment.get('gain_loss', 0):.2f}",
                f"{investment.get('percentage_change', 0):.2f}%",
                f"${investment.get('total_value', 0):.2f}"
            ]
            table_data.append(row)
        
        investment_table = Table(table_data)
        investment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(investment_table)
    
    try:
        doc.build(elements)
        print(f"PDF report generated successfully: {filename}")
    except Exception as e:
        print(f"Error generating PDF report: {e}")


def send_email_alert(uid, symbol, current_price, threshold_price, user_report):
    user = get_user_by_uid(uid)
    email = user.get('email')

    if not email:
        print(f"No email found for user {uid}")
        return

    sender_email = os.getenv("APP_EMAIL")
    sender_password = os.getenv("APP_PASS")

    subject = f"Stock Price Alert for {symbol}"
    body = f"The price of {symbol} has reached ${current_price}, which is above your threshold of ${threshold_price}.\n Attached is a summary of your current investments."

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    pdf_path = f"{uid}_investment_report.pdf"
    user_report_data = json.loads(user_report)  
    generate_pdf_report(user_report_data, pdf_path)

    try:
        with open(pdf_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {uid}_investment_report.pdf",
        )
        msg.attach(part)
    except Exception as e:
        print(f"Error attaching PDF: {e}")

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
    if not price_alerts:
        print(f"No price alerts found for user with UID {uid}.")
        return

    user_report = get_report_from_db(uid) 
    user_report_json = json.dumps(user_report)

    for symbol, thresholds in price_alerts.items():
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period='1d')
            if hist.empty:
                print(f"No historical data found for {symbol}.")
                continue

            current_price = hist['Close'].iloc[0]

            processed_thresholds = set()

            for alert_id, threshold_price in thresholds.items():
                if current_price >= threshold_price and threshold_price not in processed_thresholds:
                    send_email_alert(uid, symbol, current_price, threshold_price, user_report_json)
                    processed_thresholds.add(threshold_price)
                    db.reference(f'/users/{uid}/price_alerts/{symbol}/{alert_id}').delete()
        except Exception as e:
            print(f"Error checking price for {symbol}: {e}")
