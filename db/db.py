import firebase_admin
from firebase_admin import credentials, auth, db
import json

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('db/investmentstrack-firebase-adminsdk-s3nhe-31d8455c83.json')
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
    except auth.AuthError as e:
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
