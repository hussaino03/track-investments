import random
import spacy
import os
from spacy.training import Example


def train_model():
    model_path = "../models/model"
    if os.path.exists(model_path):
        # Load the existing model
        nlp = spacy.load(model_path)
    else:
        # Load the base model
        nlp = spacy.load("en_core_web_lg")

        # Define the training data
        TRAIN_DATA = [
            ("Put 500 in Wealthsimple, 300 in Google", {"entities": [(10, 22, "ORG"), (28, 34, "ORG")]}),
            ("I invested in Wealthsimple", {"entities": [(14, 26, "ORG")]}),
            ("Put 500 in Wealthsimple", {"entities": [(10, 22, "ORG")]}),
            ("Bought shares of MicroStrategy", {"entities": [(18, 30, "ORG")]}),
            ("Invested in a startup called TechFlow", {"entities": [(29, 37, "ORG")]}),
            ("My portfolio includes stocks from Initech", {"entities": [(37, 44, "ORG")]}),
            ("I have investments in Omni Consumer Products", {"entities": [(24, 46, "ORG")]}),
            ("Bought some stocks from Vandelay Industries", {"entities": [(26, 43, "ORG")]}),
            ("I put my money in Pied Piper", {"entities": [(20, 30, "ORG")]}),
            ("I have shares in Hooli", {"entities": [(18, 23, "ORG")]}),
            ("Invested in a small firm, E Corp", {"entities": [(27, 33, "ORG")]}),
            ("My money is in a company called Stark Industries", {"entities": [(34, 49, "ORG")]}),
        ]

        # Train the model
        train(nlp, TRAIN_DATA)

        # Save the model
        if not os.path.exists(os.path.dirname(model_path)):
            os.makedirs(os.path.dirname(model_path))
        nlp.to_disk(model_path)

    return nlp

def train(nlp, TRAIN_DATA):
    # Add the new label to ner
    ner = nlp.get_pipe("ner")
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Start the training
    nlp.begin_training()

    # Train for 15 iterations
    for itn in range(15):
        random.shuffle(TRAIN_DATA)
        losses = {}
        for text, annotations in TRAIN_DATA:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], losses=losses)
        print(losses)

train_model()
