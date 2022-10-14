import pandas as pd
import numpy as np
import json
import os
from googletrans import Translator

def load_all_messages():
    df = pd.DataFrame()

    for i in np.arange(1, len(os.listdir("messages")) + 1) : 
        file = open(os.path.join("messages", f"message_{i}.json"), encoding='utf8')
        data = json.load(file, object_hook=parse_obj)
        df_temp = pd.json_normalize(data["messages"])
        df = df.append(df_temp)

    findal_df = df[["timestamp_ms", "sender_name", "content"]]
    names = findal_df["sender_name"].unique()
    dict_map = {names[0] : 0, names[1] : 1}
    findal_df = findal_df.rename(columns={"sender_name": "sender_id"})
    findal_df["sender_id"] = findal_df["sender_id"].map(dict_map)
    findal_df = findal_df.set_index(keys="timestamp_ms", drop=True)
    findal_df = findal_df.sort_index()

    return findal_df
    
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

print(load_all_messages())