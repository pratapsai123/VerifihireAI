from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0092_emailotp_attempts'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_active',
            field=models.BooleanField(default=True, help_text='False = deactivated/offboarded. Cannot login but data preserved for audit.'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='deactivated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='deactivated_by',
            field=models.ForeignKey(blank=True, help_text='Admin who deactivated this account', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='deactivated_users', to='api.userprofile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='deactivation_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customassessment',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='Original creator — immutable audit field, not changed on ownership transfer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originally_created_custom_assessments', to='api.userprofile'),
        ),
        migrations.AddField(
            model_name='assessment',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='Original creator — immutable audit field, not changed on ownership transfer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originally_created_assessments', to='api.userprofile'),
        ),
        migrations.AddField(
            model_name='candidateinvitation',
            name='created_by',
            field=models.ForeignKey(blank=True, help_text='Original creator — immutable audit field, not changed on ownership transfer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='originally_created_invitations', to='api.userprofile'),
        ),
        migrations.CreateModel(
            name='OwnershipTransferLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transferred_at', models.DateTimeField(auto_now_add=True)),
                ('transfer_reason', models.TextField(blank=True, null=True)),
                ('assessments_transferred', models.IntegerField(default=0)),
                ('custom_assessments_transferred', models.IntegerField(default=0)),
                ('candidate_invitations_transferred', models.IntegerField(default=0)),
                ('ai_assessments_transferred', models.IntegerField(default=0)),
                ('ai_candidates_transferred', models.IntegerField(default=0)),
                ('subordinates_reassigned', models.IntegerField(default=0)),
                ('from_name', models.CharField(blank=True, max_length=255, null=True)),
                ('from_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('to_name', models.CharField(blank=True, max_length=255, null=True)),
                ('to_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('by_name', models.CharField(blank=True, max_length=255, null=True)),
                ('by_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('also_deactivated', models.BooleanField(default=False)),
                ('transferred_by', models.ForeignKey(blank=True, help_text='Admin who performed this transfer', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_initiated', to='api.userprofile')),
                ('transferred_from', models.ForeignKey(blank=True, help_text='Leaving user whose ownership was reassigned', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_from', to='api.userprofile')),
                ('transferred_to', models.ForeignKey(blank=True, help_text='Replacement user who received ownership', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transfers_to', to='api.userprofile')),
            ],
            options={
                'verbose_name': 'Ownership Transfer Log',
                'verbose_name_plural': 'Ownership Transfer Logs',
                'ordering': ['-transferred_at'],
            },
        ),
    ]
