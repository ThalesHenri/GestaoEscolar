# Generated by Django 5.1 on 2025-02-08 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_aluno_telefone_alter_aluno_responsavel_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mensalidade',
            name='desconto',
        ),
        migrations.AddField(
            model_name='mensalidade',
            name='desconto_aplicado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8),
        ),
    ]
