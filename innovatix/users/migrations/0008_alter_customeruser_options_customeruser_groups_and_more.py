# Generated by Django 5.0.1 on 2024-03-02 07:33

import django.db.models.deletion
import innovatix.geo_territories.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('geo_territories', '0001_initial'),
        ('users', '0007_company_description'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customeruser',
            options={'verbose_name': 'customer', 'verbose_name_plural': 'customers'},
        ),
        migrations.AddField(
            model_name='customeruser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into the admin panel.', verbose_name='staff status'),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='is_superuser',
            field=models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status'),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='address1',
            field=models.CharField(default='', max_length=150, verbose_name='dirección'),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='address2',
            field=models.CharField(blank=True, default='', max_length=150, verbose_name='apartamento, suite, etc.'),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='city',
            field=models.CharField(default='', max_length=75, verbose_name='ciudad'),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='province',
            field=models.ForeignKey(default=innovatix.geo_territories.utils.get_default_province, on_delete=django.db.models.deletion.PROTECT, to='geo_territories.province', verbose_name='estado'),
        ),
        migrations.AlterField(
            model_name='customeruser',
            name='zip',
            field=models.CharField(default='', max_length=5, verbose_name='código postal'),
        ),
        migrations.DeleteModel(
            name='ProgramUser',
        ),
    ]
