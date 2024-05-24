import re
import spacy
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Path to the saved model
model_path = "./models/model"

nlp = spacy.load(model_path)

def extract_investment_info(username, user_input):
    doc = nlp(user_input)

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Extract amounts
    amounts = [float(ent.text.replace('$', '').replace(',', '')) for ent in doc.ents if ent.label_ == "MONEY"]

    return {
        "entities": entities,
        "amount": amounts,
        "username": username
    }
