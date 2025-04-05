# Generated by Django 5.1.4 on 2025-04-05 04:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_remove_feedback_author_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="bot",
            field=models.CharField(
                blank=True,
                choices=[("Evo", "BasicBot"), ("EvoPro", "AdvanceBot")],
                max_length=10,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="event",
            name="event_type",
            field=models.CharField(
                choices=[("Evo", "BasicBot"), ("EvoPro", "AdvanceBot")], max_length=10
            ),
        ),
    ]
