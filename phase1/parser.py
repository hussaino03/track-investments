import re
import spacy
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from train import model_trainer

# Path to the saved model
model_path = "./models/model"

# Check if the model exists
if os.path.exists(model_path):
    # Load the saved model
    nlp = spacy.load(model_path)
else:
    # Load the base model and train it
    nlp = model_trainer.train_model()

amount_patterns = [
    r'\b\$\d+\b|\b\d+\b'
]

def extract_amount(text):
    # Initialize an empty list to store the amounts
    amounts = []

    # Iterate over each pattern in amount_patterns
    for pattern in amount_patterns:
        # Find all matches of the pattern in the text
        matches = re.findall(pattern, text)

        # Convert each match to a float and add it to the amounts list
        for match in matches:
            # Remove the dollar sign if present and convert to float
            amount = float(match.replace('$', ''))
            amounts.append(amount)

    # Return the list of amounts
    return amounts

def extract_investment_info(username, user_input):

    doc = nlp(user_input)

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Extract amount
    amounts = extract_amount(user_input)

    return {
        "entities": entities,
        "amount": amounts,
        "username": username
    }
