# Generated by Django 3.2.6 on 2021-08-18 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("predict", "0008_remove_job_queue_pos"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="task_status",
            field=models.TextField(
                default="PENDING", verbose_name="Task Status"
            ),
        ),
    ]