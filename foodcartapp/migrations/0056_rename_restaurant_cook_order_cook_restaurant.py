# Generated by Django 3.2.15 on 2022-11-21 09:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_rename_created_add_order_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='restaurant_cook',
            new_name='cook_restaurant',
        ),
    ]