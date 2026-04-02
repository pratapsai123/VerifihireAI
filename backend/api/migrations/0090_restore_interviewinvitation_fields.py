# Restores has_joined and is_completed fields to InterviewInvitation.
# These were added by a teammate in migration 0086 but were accidentally
# removed from models.py (lost during git reset) and subsequently dropped
# from the DB when makemigrations auto-generated a RemoveField in 0089.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0089_remove_interviewinvitation_has_joined_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interviewinvitation',
            name='has_joined',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='interviewinvitation',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
    ]
