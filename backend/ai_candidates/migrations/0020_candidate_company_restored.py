from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('ai_candidates', '0019_remove_candidate_company'),
        ('api', '0067_interviewinvitation_company'), # dependency on the app that has Company model
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ai_candidates', to='api.company'),
        ),
    ]
