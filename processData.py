import pandas as pd
import numpy as np
import re
import json
import os
from googletrans import Translator

def load_all_messages() -> pd.DataFrame:
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

def translate_data(data: pd.DataFrame, source_lang: str) -> pd.DataFrame:
    translator = Translator()
    data["content"] = data["content"].apply(lambda message: translator.translate(message, src=source_lang).text)    
    return data

def save_data(source_lang: str, conversation_name: str):
    data = translate_data(load_all_messages(), source_lang)
    data.to_parquet(os.path.join("preprocessed_data", f"{conversation_name}.gzip"), compression="gzip")

# to be continued
def load_data(conversation_name: str) -> pd.DataFrame:
    data = pd.read_parquet(os.path.join("preprocessed_data", f"{conversation_name}.gzip"))
    return data

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


# template call of funcion that translates from PL -> ENG and saves that convo as parquet file in
# preprocessed_data directory with the name "NS_KK.gzip"
# PS this might take a while, my 176k messages conersation has estimated 24h processing time
save_data("pl", "NS_KK")