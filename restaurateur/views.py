import requests
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from geopy import distance

from foodcartapp.models import Order, Product, Restaurant
from places.models import Place


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


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


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant in restaurants
        ]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(
        request,
        template_name="products_list.html",
        context={
            'products_with_restaurant_availability':
                products_with_restaurant_availability,
            'restaurants': restaurants,
        })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_place(api_key, address):
    place, _ = Place.objects.get_or_create(
        address=address
    )
    if not place.lon or not place.lat:
        place_coordinates = fetch_coordinates(api_key, address)
        place.lon = place_coordinates[0]
        place.lat = place_coordinates[1]
    return place


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    yandex_api_key = settings.YANDEX_API_KEY
    orders = Order.objects.all().price.get_available_restaurants()
    for order in orders:
        try:
            place = get_place(yandex_api_key, order.address)
        except request.RequestException:
            print(f'Не удалось получить координаты '
                  f'адреса доставки: {order.address}')
            order.restaurant_distances = None
            continue

        for rest in order.restaurants:
            if not rest.lon or not rest.lat:
                try:
                    rest_coordinates = fetch_coordinates(
                        yandex_api_key, rest.address
                    )
                except request.RequestException:
                    print(f'Не удалось получить координаты '
                          f'адреса ресторана: {rest.address}')
                    order.restaurant_distances = None
                    continue
                rest.lon = rest_coordinates[0]
                rest.lat = rest_coordinates[1]
                rest.save()

            rest_distance = distance.distance(
                (rest.lat, rest.lon),
                (place.lat, place.lon)
            ).km
            order.restaurant_distances.append(
                (rest.name, round(rest_distance, 2))
            )
            order.restaurant_distances = sorted(
                order.restaurant_distances, key=lambda rest_dist: rest_dist[1]
            )

    return render(request, template_name='order_items.html', context={
        'orders': orders
    })
