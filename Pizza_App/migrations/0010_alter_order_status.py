# Generated by Django 5.1.5 on 2025-05-30 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Pizza_App", "0009_drink_orderdrink"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("PENDING", "Pending"),
                    ("IN_PROGRESS", "In Progress"),
                    ("ON_THE_WAY", "On the Way"),
                    ("COMPLETED", "Completed"),
                    ("CANCELLED", "Cancelled"),
                ],
                default="PENDING",
                max_length=20,
            ),
        ),
    ]
