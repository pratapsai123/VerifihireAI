from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0031_codinginvite_codinginvitequestion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='coding_question_count',
            field=models.IntegerField(default=0, help_text='Number of coding questions attached'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='coding_total_time',
            field=models.CharField(blank=True, help_text='Total coding time in HH:MM:SS', max_length=20, null=True),
        ),
        migrations.CreateModel(
            name='AssessmentCodingQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(help_text='Display order within assessment')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('languages', models.JSONField(blank=True, default=list)),
                ('allowed_languages', models.JSONField(blank=True, default=list)),
                ('mode', models.CharField(blank=True, max_length=32, null=True)),
                ('starter_code', models.TextField(blank=True, null=True)),
                ('template_code', models.TextField(blank=True, null=True)),
                ('time_limit_ms', models.IntegerField(default=3000)),
                ('memory_limit_mb', models.IntegerField(default=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_coding_questions', to='api.assessment')),
                ('coding_question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_usages', to='api.codingquestion')),
            ],
            options={
                'verbose_name': 'Assessment Coding Question',
                'verbose_name_plural': 'Assessment Coding Questions',
                'ordering': ['assessment', 'order'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='assessmentcodingquestion',
            unique_together={('assessment', 'coding_question')},
        ),
    ]


