import json

from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.templatetags.static import static

import phonenumbers
from phonenumbers import NumberParseException
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, OrderProduct, Product


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def check_missing_data(order):
    incorrect_fields = [field for field in order.keys() if not order[field]]
    if incorrect_fields:
        raise KeyError(incorrect_fields)
    if not isinstance(order['products'], list):
        raise TypeError(f'"products" должен быть list, а получен {[type(order["products"])]}')
    phone_parsed = phonenumbers.parse(order['phonenumber'], "IN")
    if not phonenumbers.is_valid_number(phone_parsed):
        raise NumberParseException(order["phonenumber"], f'введен некорректный номер')
    return order


@api_view(['POST'])
def register_order(request):
    try:
        order = check_missing_data(request.data)
        new_order = Order.objects.create(
            firstname=order['firstname'],
            lastname=order['lastname'],
            phone=order['phonenumber'],
            address=order['address']
        )

        for item in order['products']:
            product = Product.objects.get(
                pk=item['product']
            )
            new_order_product = OrderProduct.objects.create(
                order=new_order,
                product=product,
                price=product.price,
                quantity=item['quantity']
            )
            new_order_product.save()
            new_order.products.add(product)
            new_order.save()
    except KeyError as e:
        return Response({
            'error': f'{e} - обязательно для заполненения или имеют другой тип'
        })
    except IntegrityError as e:
        return Response({
            'error': f'{e} - не может отсутствовать или быть пустым'
        })
    except TypeError as e:
        return Response({
            'error': str(e)
        })
    except ValueError as e:
        return Response({
            'error': str(e)
        })
    except NumberParseException as e:
        return Response({
            'error': str(e)
        })
    except ObjectDoesNotExist as e:
        return Response({
            'error': str(e)
        })
    return Response(order)
