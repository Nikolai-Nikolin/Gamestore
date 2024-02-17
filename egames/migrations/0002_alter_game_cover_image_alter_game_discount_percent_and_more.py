# Generated by Django 5.0.2 on 2024-02-17 03:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('egames', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='cover_image',
            field=models.ImageField(blank=True, default=None, upload_to=''),
        ),
        migrations.AlterField(
            model_name='game',
            name='discount_percent',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='discount_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='price',
            field=models.FloatField(),
        ),
    ]
