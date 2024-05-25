import json
import os
import spacy
from spacy.util import minibatch, compounding
import random
from spacy.training.example import Example
from sklearn.model_selection import train_test_split

# Define the path for saving and loading the model
model_path = "../models/model"

def read_training_data(file_path, test_size=0.2, random_state=42):
    with open(file_path, 'r', encoding='utf-8') as file:
        training_data = []
        for line in file:
            line = line.strip()
            if line:
                data = json.loads(line)
                text = data["text"]
                annotation = data["annotation"]
                training_data.append((text, {"entities": annotation}))
    # Split data into training and validation sets
    train_data, valid_data = train_test_split(training_data, test_size=test_size, random_state=random_state)
    return train_data, valid_data

# Read training data from file
train_data_file = "supervised_train.txt"
TRAIN_DATA = read_training_data(train_data_file)

def check_entity_alignment(nlp, text, entities):
    try:
        for ent in entities:
            tags = nlp.tokenizer(text).char_span(*ent[:2], label=ent[2])
            if tags is None:
                return False
        return True
    except Exception as e:
        print(f"Alignment issue with text: {text} and entities: {entities}")
        return False

def train_model(train_data, valid_data, model_path=None, n_iter=40):
    """Load the model, set up the pipeline and train the entity recognizer."""

    if os.path.exists(model_path):
        # Load the existing model
        nlp = spacy.load(model_path)
        print(f"Loaded model '{model_path}'")
    else:
        nlp = spacy.blank("en")  # create blank Language class
        print("Created blank 'en' model")

    if "ner" not in nlp.pipe_names:
        ner = nlp.add_pipe("ner")
    else:
        ner = nlp.get_pipe("ner")

    for _, annotations in train_data:
        for ent in annotations.get("entities"):
            ner.add_label(ent[2])

    # Disable other pipes to only train NER
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(train_data)
            losses = {}
            batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                examples = []
                for text, annot in zip(texts, annotations):
                    entities = annot["entities"]
                    if check_entity_alignment(nlp, text, entities):
                        examples.append(Example.from_dict(nlp.make_doc(text), annot))
                if examples:
                    nlp.update(examples, drop=0.5, losses=losses)
            print(f"Iteration {itn + 1}, Losses: {losses}")

    if model_path is not None:
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        nlp.to_disk(model_path)
        print(f"Saved model to {model_path}")

    # Evaluate on validation set
    correct_ents = 0
    total_ents = 0
    for text, annot in valid_data:
        doc = nlp(text)
        gold_ents = set(tuple(ent) for ent in annot["entities"])  # Convert each entity to a tuple
        pred_ents = set((ent.start_char, ent.end_char, ent.label_) for ent in doc.ents)  # Convert to set
        correct_ents += len(gold_ents.intersection(pred_ents))  # Count correct entities
        total_ents += len(gold_ents)

    print(f"Validation Accuracy: {correct_ents / total_ents:.2f}")

# Split data into training and validation sets
train_data, valid_data = read_training_data(train_data_file)

# Train and evaluate the model
train_model(train_data, valid_data, model_path)


# Test for validation accuracy
nlp = spacy.load(model_path)
doc = nlp("I invested $1000 in OpenAI and $2000 in Tesla")
for ent in doc.ents:
    print(ent.text, ent.label_)
