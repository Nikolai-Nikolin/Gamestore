# Generated by Django 5.0.2 on 2024-02-19 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egames', '0002_gamer_is_deleted_genre_is_deleted_review_is_deleted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamer',
            name='birth_date',
            field=models.DateField(),
        ),
    ]
