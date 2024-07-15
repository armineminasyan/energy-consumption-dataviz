from glob import glob
from os.path import basename, splitext
from typing import Optional
from pytz.exceptions import NonExistentTimeError, AmbiguousTimeError
import pandas as pd
import random
import json


WEATHER_STATIONS = '../energy/weather_stations_us.json'
COMMERCIAL_DIR = '../energy/commercial'
COMMERCIAL_COLS = {
    'Date/Time': 'datetime',
    'Electricity:Facility [kW](Hourly)': 'main',
    'Fans:Electricity [kW](Hourly)': 'fans',
    'Cooling:Electricity [kW](Hourly)': 'cooling',
    'Heating:Electricity [kW](Hourly)': 'heating',
    'InteriorLights:Electricity [kW](Hourly)': 'interior_lights',
    'InteriorEquipment:Electricity [kW](Hourly)': 'interior_equipment'
}
COMMERCIAL_BUILDINGS = {
    'FullServiceRestaurant': 'full_service_restaurant',
    'Hospital': 'hospital',
    'LargeHotel': 'large_hotel',
    'LargeOffice': 'large_office',
    'MediumOffice': 'medium_office',
    'MidriseApartment': 'midrise_apartment',
    'OutPatient': 'outpatient',
    'PrimarySchool': 'primary_school',
    'QuickServiceRestaurant': 'quick_service_restaurant',
    'SecondarySchool': 'secondary_school',
    'SmallHotel': 'small_hotel',
    'SmallOffice': 'small_office',
    'Stand-aloneRetail': 'standalone_retail',
    'StripMall': 'strip_mall',
    'SuperMarket': 'supermarket',
    'Warehouse': 'warehouse'
}


def get_ws_info(id: str, ws: dict) -> Optional[dict]:
    for station in ws:
        if station['id'] == id or station['identifiers']['wmo'] == id:
            return dict(
                name=station['name']['en'],
                state=station['region'],
                lat=station['location']['latitude'],
                lon=station['location']['longitude'],
                tz=station['timezone']
            )
    
    return None


def get_geo_info(dir: str, ws: dict) -> Optional[dict]:
    fields = basename(dir).split('_')

    assert fields[0] == 'USA'
    assert len(fields[1]) == 2 # Two-letter state code

    fields = fields[2].split('.')

    # The station code contains an extra end digit
    # compared to the WMO identifier, so we remove it.
    weather_station = fields[-1][:-1]

    return get_ws_info(id=weather_station, ws=ws)


def parse_date(date: str, info: dict) -> pd.Timestamp:
    # Sometimes this column contains a trailing whitespace.
    date = date.strip()

    year = 2023
    month = int(date[:2])
    day = int(date[3:5])
    hour = int(date[7:9])
    minute = 0
    second = 0
    tz = info['tz']

    try:
        # Timestamp wants an hour from 0 to 23.
        # Our data has hours from 1 to 24.
        # To make them compatible, we use the following trick.

        # Easy case.
        if hour < 24:
            ts = pd.Timestamp(year=year, month=month, day=day,
                                hour=hour, minute=minute, second=second,
                                tz=tz)
        else:
            # Tricky case:
            ts = pd.Timestamp(year=year, month=month, day=day,
                                hour=0, minute=minute, second=second,
                                tz=tz)
            ts += pd.Timedelta(hours=24)
    except (NonExistentTimeError, AmbiguousTimeError):
        # The data contains days when switching into and out of DST
        # (Daylight Savings Time). When DST starts, some hours are
        # repeated, i.e., we bring the clock's hands back. In this case,
        # some times are ambiguous: do they refer to the "first time"
        # the clock marked 02AM or to the second time?
        # Analogously, when DST ends, some hours are skipped, i.e.,
        # we push the clock hands forward. In this case, there are
        # times that simply do not exist.
        # The data we have available is artificially generated and
        # ignores this problem, so we have to go and fix it.
        ts = pd.Timestamp(year=year, month=month, day=day,
                            hour=hour+1, minute=minute, second=second,
                            tz=tz)

    return ts


def get_building_type(filename: str) -> str:
    for k, v in COMMERCIAL_BUILDINGS.items():
        if k in filename:
            return v
    else:
        return 'unknown'
    

def get_climate_zone(filename: str) -> str:
    name = splitext(basename(filename))[0]
    zone = name.split('_USA_')[-1]
    state, city = zone.split('_', maxsplit=1)
    city = ' '.join(city.split('_'))

    return f"{city.title()} {state}"


def set_building_info(filename: str, info: dict) -> None:
    info['building_type'] = get_building_type(filename=filename)
    info['climate_zone'] = get_climate_zone(filename=filename)


def read_commercial(filename: str, info: dict) -> pd.DataFrame:
    d = pd.read_csv(filename)
    d.rename(columns=COMMERCIAL_COLS, inplace=True)
    d.drop(columns=[c for c in d.columns if c not in COMMERCIAL_COLS.values()], inplace=True)
    d.datetime = d.datetime.apply(lambda x: parse_date(date=x, info=info))
    
    for k, v in info.items():
        d[k] = v

    return d


if __name__ == '__main__':
    sample_probability = 0.01

    with open(WEATHER_STATIONS) as f:
        ws = json.load(f)

    included_buildings = 0
    dfs = list()

    for dir in glob(f"{COMMERCIAL_DIR}/*"):
        info = get_geo_info(dir=dir, ws=ws)

        if info is None:
            continue
        
        for filename in glob(f"{dir}/*.csv"):
            if random.uniform(0.0, 1.0) > sample_probability:
                continue

            set_building_info(filename=filename, info=info)
            building_data = read_commercial(filename=filename, info=info)
            dfs.append(building_data)

            included_buildings += 1
            
            print('.', end='', flush=True)
            if included_buildings % 10 == 0:
                print(f" {included_buildings}", flush=True)

    if included_buildings % 10 != 0:
        print(f" {included_buildings}", flush=True)

    df = pd.concat(dfs)
    df.to_csv('commercial.csv', index=False)
