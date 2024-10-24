import json
import os
from geopy.distance import lonlat, distance
import requests
from dotenv import load_dotenv
import folium
from flask import Flask


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_distance(data_of_coffee_shops):
    return data_of_coffee_shops['distance']


def map():
    with open('index.html', "r", encoding='UTF-8') as file:
        return file.read()


load_dotenv()
apikey = os.getenv('GEOCODER_API_KEY')

with open('coffee.json', "r", encoding='CP1251') as coffe_shops_file:
    coffe_shops_content = coffe_shops_file.read()
coffe_shops = json.loads(coffe_shops_content)

place_of_user = input('Где вы находитесь? ', )
coordinates_of_user = fetch_coordinates(apikey, place_of_user)

treated_coffee_shops = []
for coffe_shop in coffe_shops:
    treated_coffee_shops.append({
        'title': coffe_shop['Name'],
        'distance': distance(lonlat(*coordinates_of_user), lonlat(*coffe_shop['geoData']['coordinates'])).km,
        'latitude': coffe_shop['geoData']['coordinates'][1],
        'longitude': coffe_shop['geoData']['coordinates'][0],
    })

nearest_coffee_shops = (sorted(treated_coffee_shops, key=get_distance)[:5])
m = folium.Map((coordinates_of_user[1], coordinates_of_user[0]), zoom_start=15)

group_1 = folium.FeatureGroup("coffe_shops").add_to(m)

folium.Marker(
    location=[nearest_coffee_shops[0]['latitude'], nearest_coffee_shops[0]['longitude']],
    icon=folium.Icon("red"),
    popup=nearest_coffee_shops[0]['title'],
).add_to(group_1)

folium.Marker(
    location=[nearest_coffee_shops[1]['latitude'], nearest_coffee_shops[1]['longitude']],
    icon=folium.Icon("red"),
    popup=nearest_coffee_shops[1]['title'],
).add_to(group_1)

folium.Marker(
    location=[nearest_coffee_shops[2]['latitude'], nearest_coffee_shops[2]['longitude']],
    icon=folium.Icon("red"),
    popup=nearest_coffee_shops[2]['title'],
).add_to(group_1)

folium.Marker(
    location=[nearest_coffee_shops[3]['latitude'], nearest_coffee_shops[3]['longitude']],
    icon=folium.Icon("red"),
    popup=nearest_coffee_shops[3]['title'],
).add_to(group_1)

folium.Marker(
    location=[nearest_coffee_shops[4]['latitude'], nearest_coffee_shops[4]['longitude']],
    icon=folium.Icon("red"),
    popup=nearest_coffee_shops[4]['title'],
).add_to(group_1)

m.save("index.html")

app = Flask(__name__)
app.add_url_rule('/', 'Coffee shops', map)
app.run('0.0.0.0')
