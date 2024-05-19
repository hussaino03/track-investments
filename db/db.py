from pymongo import MongoClient

# Replace <username>, <password>, and <cluster-url> with your details.
uri = "mongodb+srv://<username>:<password>@<cluster-url>/test?retryWrites=true&w=majority"

# Create a MongoClient
client = MongoClient(uri)

# Access the database
db = client["invest-tracker"]

# Access a collection (table)
collection = db["users"]

# Insert a document random just for testing
document = {"category": "Stocks", "amount": 500, "notes": "TSLA"}
collection.insert_one(document)

# Find a document
result = collection.find_one({"category": "Stocks"})
print(result)

# Update a document
collection.update_one({"category": "Stocks"}, {"$set": {"amount": 1000}})

# Delete a document
collection.delete_one({"category": "Stocks"})

# Close the connection
client.close()
