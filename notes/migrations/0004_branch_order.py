# Generated by Django 5.0.1 on 2024-02-16 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notes", "0003_remove_course_branch_course_branch"),
    ]

    operations = [
        migrations.AddField(
            model_name="branch",
            name="order",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]