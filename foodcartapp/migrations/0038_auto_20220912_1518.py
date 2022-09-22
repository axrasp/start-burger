# Generated by Django 3.2.15 on 2022-09-12 15:18

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('firstname', models.CharField(db_index=True, max_length=20, verbose_name='Имя')),
                ('lastname', models.CharField(blank=True, db_index=True, max_length=20, verbose_name='Фамилия')),
                ('created_add', models.TimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('address', models.CharField(db_index=True, max_length=100)),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='Количество')),
                ('price', models.DecimalField(decimal_places=2, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.order', verbose_name='Заказ')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_products', to='foodcartapp.product', verbose_name='Товар')),
            ],
            options={
                'verbose_name': 'Состав заказа',
                'verbose_name_plural': 'Состав заказа',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='products',
            field=models.ManyToManyField(related_name='orders', through='foodcartapp.OrderProduct', to='foodcartapp.Product', verbose_name='Товар'),
        ),
    ]