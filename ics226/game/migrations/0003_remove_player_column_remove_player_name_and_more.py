# Generated by Django 4.2.7 on 2023-11-12 05:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_player_col_player_tag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='player',
            name='column',
        ),
        migrations.RemoveField(
            model_name='player',
            name='name',
        ),
        migrations.RemoveField(
            model_name='player',
            name='score',
        ),
    ]
