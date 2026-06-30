from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0095_merge_20260410_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='customassessment',
            name='assessment_mode',
            field=models.CharField(
                choices=[('single', 'Single'), ('multiple', 'Multiple')],
                default='single',
                help_text='Single = resume-based flow, Multiple = role/sub-role based flow',
                max_length=20,
            ),
        ),
    ]
