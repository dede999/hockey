# Generated by Django 2.0.2 on 2018-04-03 03:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('h_leagues', '0007_remove_match_series'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='seed',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='team',
            name='streak',
            field=models.CharField(default='W 0', max_length=3),
        ),
    ]
