# Migration for experience_level field on Assessment model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assessments', '0021_assessment_assigned_interviewers'),
        ('ai_assessments', '0021_assessment_created_by_alter_assessment_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='experience_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('fresher', 'Fresher (0 Years)'),
                    ('entry', 'Entry (0-2 years)'),
                    ('mid', 'Mid (2-5 years)'),
                    ('senior', 'Senior (5-10 years)'),
                    ('expert', 'Expert (10+ years)'),
                ],
                help_text='Experience level for generating appropriate questions',
                max_length=20,
                null=True,
            ),
        ),
    ]
