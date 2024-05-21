import firebase_admin
from firebase_admin import credentials, auth, db

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-name.firebaseio.com'
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

if __name__ == "__main__":
    email = input("Enter email: ")
    password = input("Enter password: ")

    uid = create_user(email, password)

    if uid:
        # Example investments
        investments = [
            {"name": "Stock A", "amount": 1000},
            {"name": "Stock B", "amount": 2000}
        ]

        for investment in investments:
            add_investment_to_user(uid, investment)
        
        get_user_investments(uid)
