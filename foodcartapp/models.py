from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
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
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
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
    @property
    def price(self):
        return self.annotate(
            full_price=Sum(F('products__price')*F('order_products__quantity'))
            )


class Order(models.Model):
    phonenumber = PhoneNumberField(
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
        verbose_name='Товар',
        through='OrderProduct'
    )
    created_add = models.TimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    address = models.CharField(
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
        default=0,
        verbose_name='Cтатус'
    )
    comment = models.TextField(
        max_length=200,
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
        related_name='order_products',
        verbose_name='Заказ',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_products',
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
