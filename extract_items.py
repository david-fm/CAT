import os
import pandas as pd
import json


def extract_items(file_path):
    with open(file_path, 'r') as file:
        data = pd.read_json(path_or_buf=file_path, lines=True)
        data['text'] = data['text'].apply(json.loads)
        
        for index, row in data.iterrows():
            items = row['text']['menu']
            for item in items:
                print(item['nm'])


if __name__ == '__main__':
    extract_items('resources/results/metadata.jsonl')
    