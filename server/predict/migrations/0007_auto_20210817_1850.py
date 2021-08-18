# Generated by Django 3.2.6 on 2021-08-17 23:50

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("predict", "0006_auto_20210816_1929"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="job",
            name="completed",
        ),
        migrations.RemoveField(
            model_name="job",
            name="id",
        ),
        migrations.RemoveField(
            model_name="job",
            name="pairs",
        ),
        migrations.RemoveField(
            model_name="job",
            name="pairsIndex",
        ),
        migrations.RemoveField(
            model_name="job",
            name="seqs",
        ),
        migrations.RemoveField(
            model_name="job",
            name="seqsIndex",
        ),
        migrations.AddField(
            model_name="job",
            name="is_completed",
            field=models.BooleanField(
                default=False, verbose_name="Is Completed"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="is_running",
            field=models.BooleanField(
                default=False, verbose_name="Is Running"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="n_pairs",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Number of Pairs"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="n_pairs_done",
            field=models.PositiveIntegerField(
                blank=True, default=0, verbose_name="Number of Pairs Done"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="n_seqs",
            field=models.PositiveIntegerField(
                default=0, verbose_name="Number of Sequences"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="pair_fi",
            field=models.FilePathField(
                null=True,
                validators=[
                    django.core.validators.FileExtensionValidator(".tsv")
                ],
                verbose_name="Pair File Path",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="queue_pos",
            field=models.IntegerField(
                default=0, verbose_name="Queue Position"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="seq_fi",
            field=models.FilePathField(
                null=True,
                validators=[
                    django.core.validators.FileExtensionValidator(".fasta")
                ],
                verbose_name="Sequence File Path",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="start_time",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Start Time"
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="submission_time",
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                verbose_name="Submission Time",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="job",
            name="email",
            field=models.EmailField(
                max_length=254,
                validators=[django.core.validators.EmailValidator()],
                verbose_name="Email",
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="title",
            field=models.TextField(blank=True, verbose_name="Title"),
        ),
        migrations.AlterField(
            model_name="job",
            name="uuid",
            field=models.UUIDField(
                primary_key=True, serialize=False, verbose_name="UUID"
            ),
        ),
    ]
