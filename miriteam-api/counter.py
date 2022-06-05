import json
import os
import xlrd

def loads(filename):
    table = xlrd.open_workbook(filename, on_demand = True).sheet_by_index(0)

    result = []

    strnum = 0
    line = 0
    while strnum < table.nrows:
        row = table.row_values(strnum)
        # print(row)

        if (row[2] == 'Номер:'):
            line = 1
        elif (row[0] == 'Адрес:'):
            line = 2
        elif (row[0] == 'Повод:'):
            line = 3
        elif (row[0] == 'Диагноз:'):
            line = 4
        elif (row[0] == 'Доставлен:'):
            line = 5
        elif (row[0] == 'Принят:'):
            line = 6
        else:
            line = 0

        if (line == 1):
            record = {
                'date': None,
                'station': None
            }
            record['date'] = row[0]
        elif (line == 5):
            record['station'] = row[17]
        elif (line == 6):
            if record['station'] != None and record['station'] != '':
                result.append(record)
        else:
            pass

        # print (line)

        strnum += 1

        # if (strnum == 90):
        #     break

    return result

def load_station_files_in_one():
    folders = os.listdir('Big Data для оптимизации работы скорой помощи')
    # print(files)
    files = os.listdir(f'Big Data для оптимизации работы скорой помощи/{folders[0]}')
    res = loads(f'Big Data для оптимизации работы скорой помощи/{folders[0]}/{files[0]}')
    files.pop(0)

    for folder in folders:
        files = os.listdir(f'Big Data для оптимизации работы скорой помощи/{folder}')
        if folder == 'Журнал активных вызовов 2020':
                res = loads(f'Big Data для оптимизации работы скорой помощи/{folder}/{files[0]}')
                files.pop(0)
        for file in files:
            res += loads(f'Big Data для оптимизации работы скорой помощи/{folder}/{file}')
            # print(f'Big Data для оптимизации работы скорой помощи/{folder}/{file}' + 'loaded')

    with open('stations.json', 'w', encoding='utf-8') as ofile:
            json.dump(res, ofile, ensure_ascii=False, indent=4)

def postprocessing_stations():
    with open('stations.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # print(len(data))
    for i in range(1, len(data)):
        if data[i]['date'] == '':
            data[i]['date'] = data[i - 1]['date']


    with open('stations.json', 'w', encoding='utf-8') as ofile:
            json.dump(data, ofile, ensure_ascii=False, indent=4)

def station_counter(resp):
    # with open(f'{path}stations.json', 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    res = {}

    for record in resp:
        station = record['station']
        if station in res:
            res[station] += 1
        else:
            res |= {station: 1}

    sorted_dict = {}
    sorted_keys = sorted(res, key=res.get, reverse=True)

    for w in sorted_keys:
        sorted_dict[w] = res[w]
    
    # print(sorted_dict)
    return sorted_dict

def word_counter(path):
    with open(f'{path}/result.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    res = {}

    for record in data:
        keys = record['diagnose'].split('.|,')
        for key in keys:
            if key in res:
                res[key] += 1
            else:
                res |= {key: 1}

    sorted_mas = []
    sorted_keys = sorted(res, key=res.get, reverse=True)

    
    for w in sorted_keys:
        sorted_dict = {}
        sorted_dict['name'] = w
        sorted_dict['count'] = res[w]
        # print(sorted_dict)
        sorted_mas.append(sorted_dict)
    
    return sorted_mas
    # with open('words_in_diagnose.json', 'w', encoding='utf-8') as file:
    #     json.dump(sorted_dict, file, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    # load_station_files_in_one()
    print(word_counter(''))
    # print(station_counter(loads('Big Data для оптимизации работы скорой помощи\Журнал активных вызовов 2020\Журнал активных вызовов 01-2020.xls')))
    # station_counter('')