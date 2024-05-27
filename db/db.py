import firebase_admin
from firebase_admin import credentials, auth, db, exceptions
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(current_dir, 'investmentstrack-firebase-adminsdk-s3nhe-31d8455c83.json')

cred = credentials.Certificate(json_file_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://investmentstrack-default-rtdb.firebaseio.com/'
})

def create_user(email, password):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        print('Successfully created new user:', user.uid)
        return user.uid
    except exceptions.FirebaseError as e:
        print('Error creating new user:', e)
        return None

def add_investment_to_user(uid, investment):
    ref = db.reference(f'/users/{uid}/investments')
    ref.push(investment)
    print(f'Added investment for user {uid}: {investment}')

def get_user_investments(uid):
    ref = db.reference(f'/users/{uid}/report/investments')
    investments = ref.get()
    return investments

def save_report_to_db(uid, report):
    ref = db.reference(f'/users/{uid}/report')
    ref.set(report)
    print(f'Saved report for user {uid}')

def save_chart_to_db(uid, encoded_chart):
    db.reference(f'charts/{uid}').set(encoded_chart)

def get_report_from_db(uid):
    ref = db.reference(f'/users/{uid}/report')
    report = ref.get()
    return report

def get_chart_from_db(uid):
    chart_ref = db.reference(f'charts/{uid}')
    return chart_ref.get()

def get_user_price_alerts(uid):
    ref = db.reference(f'/users/{uid}/price_alerts')
    price_alerts = ref.get()
    print(f'\nPrice alerts for user {uid}: {price_alerts}\n')
    return price_alerts

def get_user_by_uid(uid):
    user = auth.get_user(uid)
    user_data = {
        'uid': user.uid,
        'email': user.email,
    }
    return user_data

def update_user_price_alerts(uid, symbol, threshold):
    ref = db.reference(f'/users/{uid}/price_alerts/{symbol}')
    ref.push(threshold)
    print(f'\nUpdated price alert for {uid}, {symbol}, {threshold}')

def clear_user_price_alerts(uid):
    ref = db.reference(f'/users/{uid}/price_alerts')
    ref.delete()
