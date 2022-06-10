import os
import json
import folium
from flask import Flask
import requests
from geopy import distance

API_KEY = "b5460b93-0771-4e92-92f7-1c8a7078f6c3"


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url,
                            params={
                                "geocode": address,
                                "apikey": apikey,
                                "format": "json",
                            })
    response.raise_for_status()
    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def hello_world():
    with open('index.html') as file:
        return file.read()


if __name__ == '__main__':
    input_file = open("coffee.json", "r", encoding="CP1251")
    file_contents = input_file.read()
    coffees = json.loads(file_contents)
    input_file.close()

    user_position = input("Где вы находитесь?")
    user_coordinates = fetch_coordinates(API_KEY, user_position)
    cofee_houes = [{
        "title":
        coffee["Name"],
        "distance":
        distance.distance([user_coordinates[1], user_coordinates[0]], [
            coffee["geoData"]["coordinates"][1],
            coffee["geoData"]["coordinates"][0]
        ]).km,
        "latitude":
        coffee["geoData"]["coordinates"][1],
        "longitude":
        coffee["geoData"]["coordinates"][0]
    } for coffee in coffees]

    cofee_houes.sort(key=lambda coffee: coffee["distance"])

    m = folium.Map(location=[user_coordinates[1], user_coordinates[0]],
                   zoom_start=12,
                   tiles="Stamen Terrain")

    tooltip = "Click me!"

    for coffee_house in cofee_houes[0:5]:
        folium.Marker([coffee_house["latitude"], coffee_house["longitude"]],
                      popup=coffee_house["title"],
                      tooltip=tooltip).add_to(m)

    m.save("index.html")

    app = Flask(__name__)
    app.add_url_rule('/', 'hello', hello_world)
    app.run('0.0.0.0')
