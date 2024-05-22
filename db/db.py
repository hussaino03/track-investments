import firebase_admin
from firebase_admin import credentials, auth, db, exceptions
import json, os

current_dir = os.path.dirname(os.path.abspath(__file__))

json_file_path = os.path.join(current_dir, 'investmentstrack-firebase-adminsdk-s3nhe-31d8455c83.json')

# Initialize the Firebase Admin SDK
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
    ref = db.reference(f'/users/{uid}/investments')
    investments = ref.get()
    print(f'Investments for user {uid}: {investments}')
    return investments

def save_report_to_db(uid, report):
    ref = db.reference(f'/users/{uid}/report')
    ref.set(report)
    print(f'Saved report for user {uid}')

def get_report_from_db(uid):
    ref = db.reference(f'/users/{uid}/report')
    report = ref.get()
    return report
