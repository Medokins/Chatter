#from voiceToText import record_data, convert_to_text
from nltk import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
import json

if __name__ == "__main__":
    with open("intents.json") as file:
        data = json.load(file)
    
    words = []
    labels = []
    docs = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = word_tokenize(pattern)
            words.extend(wrds)
            docs.append(pattern)
        if intent["tag"] not in labels:
            labels.append(intent["tag"]) 