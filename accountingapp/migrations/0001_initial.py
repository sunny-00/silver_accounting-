# Generated by Django 4.2.7 on 2023-12-30 08:05

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='listOfNames',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=253)),
                ('option', models.CharField(max_length=200)),
                ('mobile', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('user', models.CharField(max_length=255)),
            ],
            options={
                'unique_together': {('name', 'user', 'option')},
            },
        ),
        migrations.CreateModel(
            name='listOfAll',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login', models.CharField(max_length=200)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('narration', models.CharField(max_length=500)),
                ('weight', models.FloatField()),
                ('percentage', models.FloatField()),
                ('fine', models.FloatField()),
                ('amount', models.FloatField()),
                ('ledgeroption', models.CharField(max_length=200)),
                ('ledger', models.CharField(max_length=200)),
                ('rate', models.FloatField()),
                ('name_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accountingapp.listofnames')),
            ],
        ),
    ]
