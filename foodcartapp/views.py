import json

from django.http import JsonResponse
from django.templatetags.static import static
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


@api_view(['POST'])
def register_order(request):
    try:
        order = request.data
        if not order['products']:
            return Response({
                'error': 'products - это обязательное поле'
                         ' и не может быть пустым.'
            })
        if not type(order['products']) == list:
            return Response({
                'error': f'products - ожидался list со значениями, '
                         f'но был получен {type(order["products"])}'
            })

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
            'error': f'{e} Обязательное поле'
        })
    return Response(order)
