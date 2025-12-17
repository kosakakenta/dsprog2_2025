import requests

AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

def fetch_area_list():
    res = requests.get(AREA_URL)
    res.raise_for_status()
    return res.json()

def fetch_forecast(area_code):
    res = requests.get(FORECAST_URL.format(area_code))
    res.raise_for_status()
    return res.json()
