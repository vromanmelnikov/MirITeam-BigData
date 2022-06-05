import json

def get_forecasts():
    filename = 'full_result.json'
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    end_index = 0
    start_index = 0
    start_date = int(data[0]['date'])
    lis = []
    fore = []

    for record in data:
        if (int(record['date']) - 30 < start_date):
            lis.append(record)
            start_index += 1
            end_index += 1
        elif (record['date'] - 39 < start_date):
            fore.append(record)
            end_index += 1

    
    print(lis[0], lis[len(lis) - 1])
    print(fore[0], fore[len(fore) - 1])

get_forecasts()
    # for record in data:

# get_forecast('Журнал активных вызовов 01-2021.xls.json')
