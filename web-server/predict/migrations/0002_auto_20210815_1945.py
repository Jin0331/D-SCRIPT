# Generated by Django 3.2.4 on 2021-08-15 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("predict", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="pairs",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="job",
            name="title",
            field=models.TextField(blank=True),
        ),
    ]
