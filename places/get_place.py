from .models import Place
import requests


def get_place(api_key, address):
    place, _ = Place.objects.get_or_create(
        address=address
    )
    if not place.lon or not place.lat:
        place_coordinates = fetch_coordinates(api_key, address)
        for lon, lat in place_coordinates:
            place.lon = lon
            place.lat = lat
        place.save()
    return place


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
        return None, None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat
