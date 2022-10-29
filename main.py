#from voiceToText import record_data, convert_to_text
from nltk import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
import json
stemmer = LancasterStemmer()

import numpy as np
import json

if __name__ == "__main__":
    with open("intents.json") as file:
        data = json.load(file)
    
    words = []
    labels = []
    docs_x = []
    docs_y = []

    # intents are empty yet so this won't do anything
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])

        if intent["tag"] not in labels:
            labels.append(intent["tag"])

    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))
    labels = sorted(labels)

    training = []
    output = []

    out_empty = np.zeros(len(labels))

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w.lower()) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)

    training = np.array(training)
    output = np.array(output)