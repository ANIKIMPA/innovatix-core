# Generated by Django 5.0.1 on 2024-02-14 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='is_purchasable',
            field=models.BooleanField(default=True, help_text='Customers can purchase this even if it is not visible in the home page.', verbose_name='Purchasable'),
        ),
    ]
