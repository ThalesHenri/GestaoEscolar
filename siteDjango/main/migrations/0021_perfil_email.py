# Generated by Django 5.1 on 2025-02-18 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_remove_perfil_certificado_homologacao_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
