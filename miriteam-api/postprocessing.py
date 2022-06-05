import numpy
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import json
from geopy.geocoders import Nominatim
from datetime import datetime
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Daily

def save_file(data):
    with open('result2.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)



def getWether():
    # Set time period
    start = datetime(2020, 1, 1)
    end = datetime(2022, 5, 24)

    # Create Point for Vancouver, BC
    location = Point(56.3287, 44.002)

    # Get daily data for 2018
    data = Daily(location, start, end)
    data = data.fetch()
    result = {
        'date': None,
        'tavg': None,
        'wspd': None,
        'pres': None,
    }
    resp = []
    c = 0
    print(data.index[0].to_pydatetime())
    for i in data.index:
        result['date'] = data.index[c].to_pydatetime()
        result['date'] = result['date'].strftime('%m.%d.%Y')
        result['tavg'] = data['tavg'][c]
        result['wspd'] = data['wspd'][c]
        result['pres'] = data['pres'][c]
        resp.append(result)
        print(result)
        c = c + 1
    totxt(resp)

def totxt(data):
    with open ('toKirill.txt', 'w', encoding='utf-8') as file:
        file.write('[\n')
        for record in data:
            file.write(str(record))
            file.write('\n')
        file.write(']')
        file.close()

def load_geopos():
    with open('result.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    result = []
    count = 1
    for i in data:
        print(count)
        count = count+1
        record = i | {
                'geopos': None,
                'travel time': None,
            }
        try:
            geolocator = Nominatim(user_agent='miriteamnn')
            address = i['address'][:-7]
            address = address.replace('г.', '')
            address = address.replace('ул.', '')
            address = address.replace('д.', '')
            address = address.replace('ш.', '')
            address = address.replace(',', '')
            location = geolocator.geocode(address)
            record['geopos'] = [location.longitude, location.latitude]
        except:
            pass
        record['travel time'] = 86400 * (i['arrival'] - i['accepted'])
        result.append(record['geopos'])
    
    save_file(result)
        

if __name__ == '__main__':
    load_geopos()