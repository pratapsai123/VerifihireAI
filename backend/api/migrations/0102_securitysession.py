from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0101_contactsubmission_assessment_assessment_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecuritySession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('token', models.CharField(db_index=True, max_length=128)),
                ('user_id', models.CharField(blank=True, db_index=True, max_length=128, null=True)),
                ('session_type', models.CharField(choices=[('assessment', 'Assessment'), ('interview', 'Interview'), ('ai_assessment', 'AI Assessment'), ('ai_interview', 'AI Interview')], default='assessment', max_length=32)),
                ('status', models.CharField(choices=[('SAFE', 'SAFE'), ('VIOLATION', 'VIOLATION')], default='SAFE', max_length=16)),
                ('action', models.CharField(choices=[('CONTINUE', 'CONTINUE'), ('STOP', 'STOP')], default='CONTINUE', max_length=16)),
                ('blocked_app', models.CharField(blank=True, max_length=128, null=True)),
                ('blocked_process_name', models.CharField(blank=True, max_length=255, null=True)),
                ('blocked_app_path', models.TextField(blank=True, null=True)),
                ('reason', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_heartbeat', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='securitysession',
            index=models.Index(fields=['token'], name='api_securit_token_bf2c47_idx'),
        ),
        migrations.AddIndex(
            model_name='securitysession',
            index=models.Index(fields=['user_id'], name='api_securit_user_id_e16159_idx'),
        ),
        migrations.AddIndex(
            model_name='securitysession',
            index=models.Index(fields=['session_type', 'created_at'], name='api_securit_session_c1c62d_idx'),
        ),
    ]
