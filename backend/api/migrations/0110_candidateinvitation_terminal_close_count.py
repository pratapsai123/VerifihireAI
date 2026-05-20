from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0109_secureagentinstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateinvitation',
            name='terminal_close_count',
            field=models.PositiveSmallIntegerField(
                default=0,
                help_text='Secure Agent terminal close strikes during this invitation (max 3 before termination).',
            ),
        ),
    ]
