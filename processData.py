import pandas as pd
import numpy as np
import json
import os
from googletrans import Translator

def load_all_messages(path):
    file = open(os.path.join(path, "message_1.json"))
    data = json.load(file, object_hook=parse_obj)
    df = pd.json_normalize(data['messages'])

    if len(os.listdir("messages")) > 1:
        for i in np.arange(2, len(os.listdir("messages")) + 1) : 
            file = open(os.path.join(path, f"message_{i}.json"), encoding='utf8')
            data = json.load(file, object_hook=parse_obj)
            df_temp = pd.json_normalize(data['messages'])
            df = df.append(df_temp)
        return df
    else:
        return df
    
def parse_obj(obj):
    for key in obj:
        if isinstance(obj[key], str):
            obj[key] = obj[key].encode('latin_1').decode('utf-8')
        elif isinstance(obj[key], list):
            obj[key] = list(map(lambda x: x if type(x) != str else x.encode('latin_1').decode('utf-8'), obj[key]))
        pass
    return obj

def translate_data(data, lang):
    translator = Translator()
    translation = translator.translate(data, src=lang)
    print(f"{data} ({lang}) --> {translation.text} ({translation.dest})")

print(load_all_messages("messages"))