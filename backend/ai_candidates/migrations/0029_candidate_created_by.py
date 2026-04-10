from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0093_offboarding_and_created_by'),
        ('ai_candidates', '0028_candidate_experience_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='Original creator — immutable audit field, not changed on ownership transfer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originally_created_ai_candidates', to='api.userprofile'),
        ),
    ]
