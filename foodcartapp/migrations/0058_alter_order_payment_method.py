# Generated by Django 3.2.15 on 2022-11-21 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0057_alter_order_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.SmallIntegerField(choices=[(0, 'Наличными'), (1, 'Электронно')], db_index=True, verbose_name='Способ оплаты'),
        ),
    ]
