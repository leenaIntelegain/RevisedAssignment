# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2019-08-30 08:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0005_cartitems_order'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('restaurant', models.CharField(max_length=500)),
                ('items', models.ManyToManyField(blank=True, related_name='cart', to='restaurant.CartItems')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='restaurant.User')),
            ],
            options={
                'verbose_name_plural': 'Cart',
                'verbose_name': 'Cart',
            },
        ),
        migrations.RemoveField(
            model_name='order',
            name='items',
        ),
        migrations.AddField(
            model_name='order',
            name='Cart',
            field=models.ManyToManyField(blank=True, related_name='order', to='restaurant.Cart'),
        ),
    ]