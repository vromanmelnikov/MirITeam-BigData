import json

def word_counter():
    with open('full_result.json', 'r') as file:
        data = json.load(file)
    
    res = {}

    for record in data:
        keys = record['diagnose'].split('.|,')
        for key in keys:
            if key in res:
                res[key] += 1
            else:
                res |= {key: 1}

    
    with open('words_in_diagnose.json', 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)