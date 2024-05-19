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
document = {"name": "John", "age": 30, "city": "New York"}
collection.insert_one(document)

# Find a document
result = collection.find_one({"name": "John"})
print(result)

# Update a document
collection.update_one({"name": "John"}, {"$set": {"age": 31}})

# Delete a document
collection.delete_one({"name": "John"})

# Close the connection
client.close()
