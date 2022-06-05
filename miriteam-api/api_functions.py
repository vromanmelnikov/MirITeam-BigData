from counter import word_counter, station_counter, loads
from api_func import *
from api_functional import load_file
import json

def process_file(path, filename):
    load_file(path, filename)

def get_data(path, filename):
    data = {}

    rating = word_counter(path)
    
    # sorted(rating) 
    # рейтинг причин вызова
    data['rejting prichin vyzova'] = rating 

    # количество ложных вызовов
    data['kolichestvo lozhnyh vyzovov'] = 0

    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Вызов отменен."]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Отказ от осмотра"]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Больной не найден на месте."]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Отказ от помощи"]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. СМП не нужна."]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Адрес не найден."]
    except:
        pass
    try:
        data['kolichestvo lozhnyh vyzovov'] = data['kolichestvo lozhnyh vyzovov'] + data['rejting prichin vyzova']["Нет диагноза. Вызов отменен."]
    except:
        pass

    # график (подстанции \ количество вызовов)
    data['2'] = station_counter(loads(f'{path}/{filename}'))

    # количество вызовов
    data['3'] = get_quantity_of_calls(f'{path}/{filename}')

    # график (дата \ количество вызовов по дням/неделям)
    data['4'] = get_workload_chart(f'{path}/{filename}')

    # среднее время прибытия скорой помощи
    data['5'] = get_average_time_all(f'{path}/{filename}')

    # график (дата \ среднее время прибытия в этот день)
    data['6'] = get_average_time_by_days(f'{path}/{filename}')

    # количество превышений времени приезда
    data['7'] = get_quantity_of_lateness(f'{path}/{filename}')

    return data

    # with open(f'{path}/test_result.json', 'w', encoding='utf-8') as ofile:
    #         json.dump(data, ofile, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    process_file('1', 'Журнал активных вызовов 01-2020.xls')
    get_data('1', 'Журнал активных вызовов 01-2020.xls')