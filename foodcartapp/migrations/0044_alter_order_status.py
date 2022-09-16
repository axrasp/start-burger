# Generated by Django 3.2.15 on 2022-09-16 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Новый заказ'), (1, 'Готовится'), (2, 'Передан курьеру'), (3, 'Закрыт')], db_index=True, default=1, verbose_name='Cтатус'),
        ),
    ]
