import xlrd
import json
import os
import datetime

from xlrd.xldate import xldate_as_datetime

def load(pyth_with_filename):
    filename = pyth_with_filename

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
                'id': None,
                'age': None,
                'called': None,
                'address': None,
                'reason': None,
                'twice': None,
                'type': None,
                'diagnose': None,
                'result': None,
                'delivered': None,
                'accepted': None,
                'arrival': None
            }
            record['date'] = row[0]
            if record['date'] != '':
                python_datetime = xldate_as_datetime(float(record['date']), 0)
                record['date'] = python_datetime.strftime('%d.%m.%Y')
            record['id'] = row[3]
            record['age'] = row[16]
            record['called'] = row[19]
        elif (line == 2):
            record['address'] = row[1]
        elif (line == 3):
            record['reason'] = row[1]
            record['twice'] = row[11]
            if record['twice'] == 'Первичный':
                record['twice'] = 0
            else:
                record['type'] = 1
            record['type'] = row[18]

            if record['type'] == 'неотложное состояние':
                record['type'] = 1
            else:
                record['type'] = 0
        elif (line == 4):
            record['diagnose'] = row[1]
            record['result'] = row[11]
        elif (line == 5):
            record['delivered'] = row[1]
        elif (line == 6):
            record['accepted'] = row[8]
            record['arrival'] = row[11]
            if record['date'] is not None:
                result.append(record)
        else:
            pass

        # print (line)

        strnum += 1

        # if (strnum == 90):
        #     break

    return result

def load_files():
    files = os.listdir('dataset')
    print(files)

    for file in files:
        with open(file + '.json', 'w', encoding='utf-8') as ofile:
            json.dump(load(file), ofile, ensure_ascii=False,  indent=4)

def load_files_in_one():
    folders = os.listdir('Big Data для оптимизации работы скорой помощи')
    # print(files)
    files = os.listdir(f'Big Data для оптимизации работы скорой помощи/{folders[0]}')
    res = load(f'Big Data для оптимизации работы скорой помощи/{folders[0]}/{files[0]}')
    files.pop(0)

    for folder in folders:
        files = os.listdir(f'Big Data для оптимизации работы скорой помощи/{folder}')
        if folder == 'Журнал активных вызовов 2020':
                res = load(f'Big Data для оптимизации работы скорой помощи/{folder}/{files[0]}')
                files.pop(0)
        for file in files:
            res += load(f'Big Data для оптимизации работы скорой помощи/{folder}/{file}')
            print(f'Big Data для оптимизации работы скорой помощи/{folder}/{file}' + 'loaded')

    with open('full_result.json', 'w', encoding='utf-8') as ofile:
            json.dump(res, ofile, ensure_ascii=False, indent=4)


def postprocessing():
    with open('full_result.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    for i in range(len(data)):
        if data[i]['date'] == '':
            data[i]['date'] = data[i - 1]['date']
        

    with open('full_result.json', 'w', encoding='utf-8') as ofile:
            json.dump(data, ofile, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    load_files_in_one()