import json
import load
import diagnose

def load_file(path, filename):
    with open(f'{path}/result.json', 'w', encoding='utf-8') as file:
        json.dump(load.load(f'{path}/{filename}'), file, ensure_ascii=False, indent=4)

def load_files():
    load.load_files()

def load_files_in_one():
    load.load_files_in_one()

def diagnose_word_counter():
    diagnose.word_counter()