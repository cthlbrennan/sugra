# Generated by Django 5.1.1 on 2024-11-07 23:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0012_alter_game_price_reviewvote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='genre',
            field=models.CharField(choices=[('Action Adventure', 'Action Adventure Game'), ('Action RPG', 'Action RPG'), ('Adventure', 'Adventure'), ('Casual', 'Casual'), ('Fighting', 'Fighting'), ('First Person Shooter', 'First Person Shooter'), ('Massively Multiplayer Online', 'Massively Multiplayer Online'), ('Platformer', 'Platformer'), ('Puzzle', 'Puzzle'), ('Party', 'Party'), ('Racing', 'Racing'), ('RPG', 'RPG'), ('Sandbox', 'Sandbox'), ('Shooter', 'Shooter'), ('Simulation', 'Simulation'), ('Stealth', 'Stealth'), ('Strategy', 'Strategy'), ('Survival Horror', 'Survival Horror'), ('Sports', 'Sports')], max_length=100),
        ),
        migrations.AlterField(
            model_name='reviewvote',
            name='vote_type',
            field=models.CharField(choices=[('Upvote', 'Upvote'), ('Downvote', 'Downvote')], max_length=8),
        ),
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(blank=True, choices=[('Gamer', 'Gamer'), ('Developer', 'Developer'), ('Admin', 'Admin')], max_length=10, null=True),
        ),
    ]
