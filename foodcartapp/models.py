from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator


class Restaurant(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )
    address = models.CharField(
        'Адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'Контактный телефон',
        max_length=50,
        blank=True,
    )
    lon = models.FloatField(
        'Координата ресторана (Долгота)',
        validators=[
            MaxValueValidator(-180),
            MinValueValidator(180)
        ],
        blank=True,
        null=True
    )
    lat = models.FloatField(
        'Координата ресторана (Широта)',
        validators=[
            MaxValueValidator(-90),
            MinValueValidator(90)
        ],
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='Категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'Цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'Картинка'
    )
    special_status = models.BooleanField(
        'Спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'Описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='Ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='Продукт',
    )
    availability = models.BooleanField(
        'В продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class PriceQuerySet(models.QuerySet):
    def get_available_restaurants(self):
        orders = self.prefetch_related('products')

        menu_items_available = RestaurantMenuItem.objects.filter(
            availability=True
        ).select_related('restaurant', 'product')

        for order in orders:
            order.restaurant_distances = []
            order.restaurants = set()

            for order_item in order.products.all():
                product_restaurants = [
                    rest_item.restaurant for rest_item in menu_items_available
                    if order_item.id == rest_item.product.id
                ]

                if not order.restaurants:
                    order.restaurants = set(product_restaurants)
                order.restaurants &= set(product_restaurants)
        return orders

    def get_full_price(self):
        return self.annotate(
            full_price=Sum(F('products__price')*F('products_ordered__quantity'))
            )


class Order(models.Model):
    phonenumber = PhoneNumberField(
        verbose_name='Номер телефона'
    )
    firstname = models.CharField(
        max_length=20,
        verbose_name='Имя',
        db_index=True
    )
    lastname = models.CharField(
        max_length=20,
        verbose_name='Фамилия',
        blank=True,
        db_index=True
    )
    products = models.ManyToManyField(
        Product,
        related_name='orders',
        verbose_name='Товары',
        through='OrderProduct'
    )
    created_at = models.TimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    address = models.CharField(
        verbose_name='Адрес',
        max_length=100,
        db_index=True
    )
    status = models.SmallIntegerField(
        choices=[
            (0, 'Новый заказ'),
            (1, 'Готовится'),
            (2, 'Передан курьеру'),
            (3, 'Закрыт')
        ],
        db_index=True,
        verbose_name='Cтатус'
    )
    payment_method = models.SmallIntegerField(
        choices=[
            (0, 'Наличными'),
            (1, 'Электронно'),
        ],
        db_index=True,
        verbose_name='Способ оплаты'
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True
    )
    registered_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата/время создания',
        db_index=True
    )
    called_at = models.DateTimeField(
        verbose_name='Дата/время звонка',
        db_index=True,
        null=True,
        blank=True
    )
    delivered_at = models.DateTimeField(
        verbose_name='Дата/время доставки',
        db_index=True,
        null=True,
        blank=True
    )
    cook_restaurant = models.ForeignKey(
        Restaurant,
        related_name="orders",
        on_delete=models.SET_NULL,
        verbose_name="Ресторан",
        null=True,
        blank=True,
    )
    objects = PriceQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} - {self.pk}'


class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products_ordered',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='products_ordered',
        verbose_name='Товар',
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(1)
        ],
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=8,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )

    class Meta:
        verbose_name = 'Состав заказа'
        verbose_name_plural = 'Состав заказа'

    def __str__(self):
        return f'{self.product} {self.quantity} шт.'
