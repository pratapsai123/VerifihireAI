from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0114_candidatedetails_identity_mismatch_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateinvitation',
            name='claimed_session_last_seen',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Last heartbeat timestamp from the active exam tab (used to detect stale locks).',
            ),
        ),
    ]
