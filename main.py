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


def load_map():
    with open('index.html', "r", encoding='UTF-8') as file:
        return file.read()


def load_coffee_shops(filepath):
    with open(f'{filepath}', "r", encoding='CP1251') as file:
        return json.loads(file.read())


def main():
    load_dotenv()
    apikey = os.getenv('GEOCODER_API_KEY')

    coffe_shops = load_coffee_shops('coffee.json')

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

    folium.Marker(
        location=[coordinates_of_user[1], coordinates_of_user[0]],
        icon=folium.Icon(color="green", icon='hand-peace',prefix= 'fa',icon_color='black'),
        popup='I\'m here!',
    ).add_to(m)

    group_1 = folium.FeatureGroup("coffe_shops").add_to(m)
    for coffee_shop in nearest_coffee_shops:
        folium.Marker(
            location=[coffee_shop['latitude'], coffee_shop['longitude']],
            icon=folium.Icon(color="blue", icon='coffee',prefix= 'fa',icon_color='black'),
            popup=coffee_shop['title'],
        ).add_to(group_1)

    m.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'Coffee shops', load_map)
    app.run('0.0.0.0')


if __name__ == '__main__':
    main()
