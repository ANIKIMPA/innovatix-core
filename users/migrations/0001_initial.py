# Generated by Django 4.2.3 on 2023-10-05 03:05

import core.services.phone_number_service
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import geo_territories.utils
import users.models.base_user
import users.models.program_user


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('geo_territories', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=75, verbose_name='full name')),
                ('email', models.EmailField(max_length=100, verbose_name='email address')),
                ('phone_number', models.CharField(max_length=17, validators=[core.services.phone_number_service.PhoneNumberService.validate_phone_number], verbose_name='phone number')),
                ('message', models.TextField(verbose_name='message')),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=50, unique=True, verbose_name='text')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ['text'],
            },
        ),
        migrations.CreateModel(
            name='CustomerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, help_text='Required. 150 characters or fewer.', max_length=150, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=72, verbose_name='first name')),
                ('last_name', models.CharField(max_length=72, verbose_name='last name')),
                ('phone_number', models.CharField(blank=True, max_length=17, validators=[core.services.phone_number_service.PhoneNumberService.validate_phone_number], verbose_name='phone number')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('external_customer_id', models.CharField(blank=True, max_length=50, verbose_name='Stripe ID')),
                ('partner_number', models.CharField(blank=True, max_length=20, unique=True, validators=[django.core.validators.RegexValidator(code='invalid_partner_number', message="Partner number must be in the format: 'YYYY-MM-####'", regex='^\\d{4}-\\d{2}-\\d{4}$')], verbose_name='partner number')),
                ('accept_email_marketing', models.BooleanField(default=True, verbose_name='Customer agreed to receive marketing emails.')),
                ('accept_sms_marketing', models.BooleanField(default=True, help_text='You should ask your customers for permission before you subscribe them to your marketing emails or SMS.', verbose_name='Customer agreed to receive SMS marketing text messages.')),
                ('accept_terms_condition', models.BooleanField(default=False, verbose_name='Customer agreed to the Terms and Conditions.')),
                ('company', models.CharField(blank=True, max_length=75, verbose_name='company')),
                ('address1', models.CharField(max_length=150, verbose_name='address')),
                ('address2', models.CharField(blank=True, max_length=150, verbose_name='apartment, suite, etc.')),
                ('city', models.CharField(max_length=75, verbose_name='city')),
                ('zip', models.CharField(max_length=5, verbose_name='zip code')),
                ('notes', models.TextField(blank=True, help_text='Add notes about your customer.', verbose_name='notes')),
                ('langugage', models.CharField(choices=[('spanish', 'Spanish'), ('english', 'English')], default='spanish', max_length=30, verbose_name='langugage')),
                ('pay_tax', models.BooleanField(default=True, verbose_name='Collect tax')),
                ('country', models.ForeignKey(default=geo_territories.utils.get_default_country, on_delete=django.db.models.deletion.PROTECT, to='geo_territories.country')),
                ('province', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='geo_territories.province', verbose_name='state')),
                ('tags', models.ManyToManyField(blank=True, help_text='Tags can be used to categorize customers into groups.', to='users.tag')),
            ],
            options={
                'verbose_name': 'customer',
                'verbose_name_plural': 'customers',
            },
            managers=[
                ('objects', users.models.base_user.BaseUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ProgramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(error_messages={'unique': 'A user with that email already exists.'}, help_text='Required. 150 characters or fewer.', max_length=150, unique=True, verbose_name='email address')),
                ('first_name', models.CharField(max_length=72, verbose_name='first name')),
                ('last_name', models.CharField(max_length=72, verbose_name='last name')),
                ('phone_number', models.CharField(blank=True, max_length=17, validators=[core.services.phone_number_service.PhoneNumberService.validate_phone_number], verbose_name='phone number')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'program manager',
                'verbose_name_plural': 'program managers',
            },
            managers=[
                ('objects', users.models.program_user.ProgramUserManager()),
            ],
        ),
    ]
