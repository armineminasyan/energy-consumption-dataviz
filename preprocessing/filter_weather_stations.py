import json


if __name__ == '__main__':
    with open('../energy/weather_stations.json') as f:
        ws = json.load(f)

    ws = [station for station in ws if station['country'] == 'US']

    with open('../energy/weather_stations_us.json', mode='w') as f:
        json.dump(ws, f)
