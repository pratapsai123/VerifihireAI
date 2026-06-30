from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ai_assessments', '0018_merge_20260312_1225'),
        ('api', '0067_interviewinvitation_company'), # dependency on the app that has Company model
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_assessments', to='api.company'),
        ),
    ]
