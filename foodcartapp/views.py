from django.db import transaction
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


class ProductsSerializer(ModelSerializer):

    class Meta:
        model = OrderProduct
        fields = [
            'product',
            'quantity'
        ]


class OrderSerializer(ModelSerializer):
    products = ProductsSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    def create(self, validated_data):
        validated_data.pop('products')
        new_order = Order.objects.create(**validated_data)
        return new_order

    class Meta:
        model = Order
        fields = [
            'phonenumber',
            'firstname',
            'lastname',
            'address',
            'products'
        ]


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_products = serializer.validated_data['products']
    new_order = serializer.save()

    new_order_products = [
        OrderProduct(order=new_order,
                     product=product['product'],
                     quantity=product['quantity'],
                     price=Product.objects.get(pk=product['product'].id).price)
        for product in new_products
    ]

    OrderProduct.objects.bulk_create(new_order_products)
    new_order_serialized = OrderSerializer(new_order)

    return Response(new_order_serialized.data)
