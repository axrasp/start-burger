from models import Place
from restaurateur.views import fetch_coordinates


def get_place(api_key, address):
    place, _ = Place.objects.get_or_create(
        address=address
    )
    if not place.lon or not place.lat:
        place_coordinates = fetch_coordinates(api_key, address)
        place.lon = place_coordinates[0]
        place.lat = place_coordinates[1]
    return place
