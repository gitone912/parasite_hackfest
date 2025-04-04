# Generated by Django 5.1.4 on 2025-04-05 03:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_event"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Feedback",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tag", models.CharField(max_length=200)),
                ("tweet_text", models.TextField()),
                ("tweet_date", models.DateTimeField()),
                ("search_date", models.DateTimeField(auto_now_add=True)),
                ("sentiment", models.CharField(blank=True, max_length=20, null=True)),
                ("tweet_id", models.CharField(max_length=100)),
                ("author_username", models.CharField(max_length=100)),
                (
                    "event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app.event",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
