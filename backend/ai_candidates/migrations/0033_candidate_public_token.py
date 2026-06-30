from django.db import migrations, models
import uuid

def gen_uuid(apps, schema_editor):
    Candidate = apps.get_model('ai_candidates', 'Candidate')
    for row in Candidate.objects.all():
        row.public_token = uuid.uuid4()
        row.save(update_fields=['public_token'])

class Migration(migrations.Migration):

    dependencies = [
        ('ai_candidates', '0032_candidate_batch_name_alter_candidate_batch_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='public_token',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='candidate',
            name='public_token',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True, null=False),
        ),
    ]
