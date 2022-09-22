from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Place(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True,
    )
    created_add = models.TimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    lon = models.FloatField(
        'Координата адреса (Долгота)',
        validators=[
            MaxValueValidator(-180),
            MinValueValidator(180)
        ],
        blank=True,
        null=True
    )
    lat = models.FloatField(
        'Координата адреса (Широта)',
        validators=[
            MaxValueValidator(-90),
            MinValueValidator(90)
        ],
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Адрес заказа'
        verbose_name_plural = 'Адреса заказов'

    def __str__(self):
        return self.address
