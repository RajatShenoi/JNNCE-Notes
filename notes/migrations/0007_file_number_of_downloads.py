# Generated by Django 5.0.1 on 2024-02-16 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0006_remove_coursemodule_number_of_files"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="number_of_downloads",
            field=models.IntegerField(default=0),
        ),
    ]
