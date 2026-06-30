from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0108_qualification_request'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecureAgentInstance',
            fields=[
                ('instance_id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('first_token', models.CharField(db_index=True, max_length=128)),
                ('consumed', models.BooleanField(db_index=True, default=False)),
                ('consumed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
