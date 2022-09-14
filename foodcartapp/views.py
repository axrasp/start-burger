from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        Serializer, ValidationError)

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


class ProductsSerializer(Serializer):
    product = IntegerField(min_value=1)
    quantity = IntegerField(min_value=1)

    def validate_product(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise ValidationError(f'Недопустимый первичный '
                                  f'ключ product : {value}')
        return value


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'phonenumber',
            'firstname',
            'lastname',
            'address',
            'products'
        ]


@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order_serialized = serializer.validated_data

    new_order = Order.objects.create(
        firstname=order_serialized['firstname'],
        lastname=order_serialized['lastname'],
        phonenumber=order_serialized['phonenumber'],
        address=order_serialized['address']
    )

    products_serialized = order_serialized['products']
    new_order_products = [
        OrderProduct(order=new_order,
                     product=Product.objects.get(pk=product['product']),
                     quantity=product['quantity'])
        for product in products_serialized
    ]
    OrderProduct.objects.bulk_create(new_order_products)

    new_order_serialized = OrderSerializer(new_order)

    return Response(new_order_serialized.data)
