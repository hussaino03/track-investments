import re
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

# Regular expressions for extracting amounts
amount_patterns = [
    r"\$\d+(\.\d{1,2})?",     # $500 or $500.00
    r"\d+(\.\d{1,2})?\s*dollars",  # 500 dollars or 500.00 dollars
    r"\d+\s*bands",           # 5 bands (slang)
]

def extract_amount(text):
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    return None

def extract_investment_info(user_input):
    doc = nlp(user_input)

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in doc.ents]

    # Extract amount
    amount = extract_amount(user_input)

    return {
        "entities": entities,
        "amount": amount
    }