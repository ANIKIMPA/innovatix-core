# Generated by Django 5.0.1 on 2024-02-13 16:20

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_alter_payment_status_alter_paymentmethod_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='subtotal',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='subtotal'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='tax',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='tax'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='total',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='total'),
        ),
    ]