# Generated by Django 5.1.1 on 2024-10-16 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('gamer', 'Gamer'), ('developer', 'Developer')], max_length=20),
        ),
    ]