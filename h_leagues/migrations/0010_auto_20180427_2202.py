# Generated by Django 2.0.2 on 2018-04-27 22:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('h_leagues', '0009_auto_20180425_2202'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='participation',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='participation',
            name='series',
        ),
        migrations.RemoveField(
            model_name='participation',
            name='team',
        ),
        migrations.AlterUniqueTogether(
            name='postseason',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='postseason',
            name='participates',
        ),
        migrations.RemoveField(
            model_name='postseason',
            name='season',
        ),
        migrations.RemoveField(
            model_name='postseason',
            name='team',
        ),
        migrations.RemoveField(
            model_name='psmatch',
            name='season',
        ),
        migrations.AlterUniqueTogether(
            name='series',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='series',
            name='league',
        ),
        migrations.RemoveField(
            model_name='series',
            name='season',
        ),
        migrations.DeleteModel(
            name='Participation',
        ),
        migrations.DeleteModel(
            name='PostSeason',
        ),
        migrations.DeleteModel(
            name='PSMatch',
        ),
        migrations.DeleteModel(
            name='Series',
        ),
    ]
