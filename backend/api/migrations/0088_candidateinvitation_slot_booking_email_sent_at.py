from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0087_merge_20260331_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateinvitation',
            name='slot_booking_email_sent_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text='Timestamp when the slot-booking email was dispatched. Used to compute the candidate\'s booking window.'
            ),
        ),
    ]
