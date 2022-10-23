import pandas as pd
import numpy as np
import re
import json
import os
from googletrans import Translator

def load_all_messages() -> pd.DataFrame():
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

# just for easier testing
def print_conversation(data):
    section_flag = data.iloc[0]["is_sender"]
    for i in range(len(data) - 1):
        if section_flag != data.iloc[i]["is_sender"]:
            section_flag = data.iloc[i]["is_sender"]
            print("")
        if data.index[i+1] - data.index[i] > 360000 * 7:
            print(15 * "*", " Another conversation ", 15 * "*")

        print(data.iloc[i]["content"])

# use only if your data isn't already in english!
# Due to unstable state of googletrans I recommend translating data in 500messages packages
# and checking every now and then if it's till going, if not just paste last range value as satrt index in function call
def translate(source_lang: str, conversation_name: str, iter_range: int, start_index = 0):
    import time
    translator = Translator()

    def translate_data(data: pd.DataFrame, source_lang: str):
        data["content"] = data["content"].apply(lambda message: translator.translate(message, src=source_lang).text)    
        return data

    def save_cut_data(source_lang: str, conversation_name: str, iter_range):
        data = translate_data(load_all_messages()[iter_range[0]:iter_range[1]], source_lang)
        data.to_parquet(os.path.join("preprocessed_data", f"{conversation_name}_{iter_range[0]}-{iter_range[1]}.gzip"), compression="gzip")

    for i in range(start_index, len(load_all_messages()), iter_range):
        save_cut_data(source_lang, conversation_name, [i, i + 500])
        if i%1000 == 0:
            # sleep to not surpass requests limit
            time.sleep(30)
            print(f"Sleeping at {i}")

# use only if You had translated Your data:
def join_data(conversation_name):
    from pathlib import Path
    data_dir = Path("preprocessed_data")
    if len([file for file in data_dir.glob('*.gzip')]) == 0:
        print("there are no files in preprocessed_data directory! Translate data first (Use translate() function)")
    else:
        full_df = pd.concat(
            pd.read_parquet(parquet_file)
            for parquet_file in data_dir.glob('*.gzip')
        )
        full_df.to_parquet(os.path.join("full_conversations", f"{conversation_name}.parquet"))
        # moving files to bin
        for file in data_dir.glob('*.gzip'):
            os.replace(file, os.path.join("bin", file.name))

def save_data(conversation_name, translated = False):
    if not translated:
        data = load_all_messages()
        data.to_parquet(os.path.join("full_conversations", f"{conversation_name}.parquet"))
    else:
        join_data(conversation_name)

def load_data(conversation_name: str) -> pd.DataFrame():
    data = pd.read_parquet(os.path.join("full_conversations", f"{conversation_name}.parquet"))
    return data

# sample call for save_data() function after processed_data is filled with translated cuts of conversation:
# save_data("NS_KK_translated", translated=True)

# sample call for save_data() function when Your conversation is already in english:
# save_data("NS_KK_original")
          