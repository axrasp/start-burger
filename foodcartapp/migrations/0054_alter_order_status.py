# Generated by Django 3.2.15 on 2022-10-01 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0053_rename_restaurant_order_restaurant_cook'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Новый заказ'), (1, 'Готовится'), (2, 'Передан курьеру'), (3, 'Закрыт')], db_index=True, verbose_name='Cтатус'),
        ),
    ]