# Generated migration for invited candidates tracking

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assessments', '0026_assessment_same_questions_for_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='max_candidates_allowed',
            field=models.IntegerField(default=1, help_text='Maximum number of candidates that can be invited to this assessment'),
        ),
        migrations.CreateModel(
            name='InvitedCandidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('invited_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('invited', 'Invited'), ('started', 'Started'), ('completed', 'Completed'), ('declined', 'Declined')], default='invited', max_length=20)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_candidates', to='ai_assessments.assessment')),
            ],
            options={
                'db_table': 'ai_invited_candidate',
            },
        ),
        migrations.AlterUniqueTogether(
            name='invitedcandidate',
            unique_together={('assessment', 'email')},
        ),
    ]
