import random
import spacy
import os
from spacy.training import Example
from spacy.util import minibatch, compounding

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
            ("Put 500 in Wealthsimple and 200 in Google", {"entities": [(10, 22, "ORG"), (27, 33, "ORG")]}),
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
            ("invested $500 in Tesla", {"entities": [(14, 19, "ORG")]}),
            ("yo whatsup I just invested 5 bands into Tesla right now", {"entities": [(37, 42, "ORG")]}),
            ("I just put $1200 into Apple stocks", {"entities": [(23, 28, "ORG")]}),
            ("Added 2000 dollars to Microsoft investment", {"entities": [(24, 33, "ORG")]}),
            ("Just dropped $300 on Amazon shares", {"entities": [(18, 24, "ORG")]}),
            ("Invested in Google and Apple today", {"entities": [(11, 17, "ORG"), (22, 27, "ORG")]}),
            ("Bought stocks of Tesla and Amazon", {"entities": [(16, 21, "ORG"), (26, 32, "ORG")]}),
            ("Invested $200 in Google and $300 in Amazon", {"entities": [(15, 21, "ORG"), (31, 37, "ORG")]}),
            ("I have invested in Wealthsimple and Google", {"entities": [(21, 33, "ORG"), (38, 44, "ORG")]}),
            ("Investments in Apple, Tesla, and Google", {"entities": [(15, 20, "ORG"), (22, 27, "ORG"), (33, 39, "ORG")]}),
            ("Google is my favorite company", {"entities": [(0, 6, "ORG")]}),
        ]

        # Add NER pipeline if it's not already present
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner", last=True)
        else:
            ner = nlp.get_pipe("ner")

        # Add new entity labels to the NER pipeline
        for _, annotations in TRAIN_DATA:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])

        # Disable other pipelines to train only NER
        pipe_exceptions = ["ner"]
        unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

        with nlp.disable_pipes(*unaffected_pipes):
            # Initialize the optimizer
            optimizer = nlp.begin_training()

            # Train for 40 iterations
            for itn in range(40):
                random.shuffle(TRAIN_DATA)
                losses = {}
                # Use minibatch and compounding to generate batches
                batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    examples = [Example.from_dict(nlp.make_doc(text), annotation) for text, annotation in zip(texts, annotations)]
                    nlp.update(examples, drop=0.5, losses=losses, sgd=optimizer)
                print(f"Iteration {itn + 1} - Losses: {losses}")

        # Save the model
        if not os.path.exists(os.path.dirname(model_path)):
            os.makedirs(os.path.dirname(model_path))
        nlp.to_disk(model_path)

    return nlp

if __name__ == "__main__":
    train_model()
