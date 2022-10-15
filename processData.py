import pandas as pd
import numpy as np
import re
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

    final_df = df[["timestamp_ms", "sender_name", "content"]]
    final_df = final_df.dropna()

    # set timestamp_ms as index
    final_df = final_df.set_index(keys="timestamp_ms", drop=True)
    final_df = final_df.sort_index()

    # change to bool to be faster/lighter
    names = final_df["sender_name"].unique()
    dict_map = {names[0] : 0, names[1] : 1}
    final_df = final_df.rename(columns={"sender_name": "is_sender"})
    final_df["is_sender"] = final_df["is_sender"].map(dict_map).astype(np.bool)

    # change to string to be faster/lighter
    final_df["content"] = final_df["content"].astype("string")

    # remove links
    final_df["content"] = final_df["content"].apply(lambda x: re.split('https:\/\/.*', str(x))[0])
    final_df["content"] = final_df["content"].replace('', np.NaN)
    final_df = final_df.dropna()

    return final_df

# to correct Facebook's wrong encoding of foreign letters.  
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

df = load_all_messages()
print(df)