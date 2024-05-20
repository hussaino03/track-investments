from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://apptestingphone1:mnd0qljGSUZ4OCKw@investtracker.suvl2bt.mongodb.net/?retryWrites=true&w=majority&appName=investtracker"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Access the database
db = client.investtracker

# Create a new user document
user = {
    "username": "johndoe",
    "email": "johndoe@example.com",
    "investments": [
        {"type": "stock", "amount": 50, "notes": "tesla"},
        {"type": "crypto", "amount": 50, "notes": "btc"}
    ]
}

# Insert the user into the 'users' collection
users_collection = db.users
try:
    result = users_collection.insert_one(user)
    print(f"User inserted with _id: {result.inserted_id}")
except Exception as e:
    print(e)

# Retrieve and display the user to confirm the insertion
try:
    inserted_user = users_collection.find_one({"_id": result.inserted_id})
    print(f"Inserted user: {inserted_user}")
except Exception as e:
    print(e)
