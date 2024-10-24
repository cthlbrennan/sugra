# Generated by Django 5.1.1 on 2024-10-24 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_user_user_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(blank=True, choices=[('gamer', 'Gamer'), ('developer', 'Developer'), ('admin', 'Admin')], max_length=10, null=True),
        ),
    ]