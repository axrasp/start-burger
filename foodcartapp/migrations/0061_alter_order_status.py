# Generated by Django 3.2.15 on 2022-11-22 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_order_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Новый заказ'), (1, 'Готовится'), (2, 'Передан курьеру'), (3, 'Закрыт')], db_index=True, default=0, verbose_name='Cтатус'),
        ),
    ]
