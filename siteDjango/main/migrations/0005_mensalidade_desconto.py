# Generated by Django 5.1 on 2025-02-05 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_feed'),
    ]

    operations = [
        migrations.AddField(
            model_name='mensalidade',
            name='desconto',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=8, null=True),
        ),
    ]
