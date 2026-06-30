"""
Django models for DeepFace Proctoring tables.

These models define the database schema for the deepface microservice.
The deepface FastAPI service reads/writes these tables via raw asyncpg,
but Django manages the schema via migrations.
"""

from django.db import models


class DeepfaceSession(models.Model):
    """Monitoring session tracking."""
    session_id = models.CharField(max_length=255, unique=True)
    person_id = models.CharField(max_length=255, db_index=True)
    status = models.CharField(max_length=50, default='active', db_index=True)
    started_at = models.CharField(max_length=50, null=True, blank=True)
    ended_at = models.CharField(max_length=50, null=True, blank=True)
    config = models.TextField(default='{}')
    camera_device = models.CharField(max_length=255, null=True, blank=True)
    total_frames = models.IntegerField(default=0)
    total_violations = models.IntegerField(default=0)
    verification_attempts = models.IntegerField(default=0)
    verification_successes = models.IntegerField(default=0)
    engagement_sum = models.FloatField(default=0.0)
    avg_engagement = models.FloatField(default=0.0)
    min_engagement = models.FloatField(default=100.0)
    max_engagement = models.FloatField(default=0.0)
    micro_violation_score = models.FloatField(default=0.0)

    class Meta:
        db_table = 'deepface_sessions'

    def __str__(self):
        return f"Session {self.session_id} ({self.person_id}) - {self.status}"


class DeepfaceViolation(models.Model):
    """Violation events logged during a session."""
    session = models.ForeignKey(
        DeepfaceSession,
        to_field='session_id',
        db_column='session_id',
        on_delete=models.CASCADE,
        related_name='violations',
    )
    type = models.CharField(max_length=100)
    severity = models.CharField(max_length=50)
    message = models.TextField(null=True, blank=True)
    timestamp = models.CharField(max_length=50, null=True, blank=True)
    details = models.TextField(null=True, blank=True)
    frame_snapshot = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'deepface_violations'

    def __str__(self):
        return f"[{self.severity}] {self.type} @ {self.timestamp}"


class DeepfaceEngagementSnapshot(models.Model):
    """Engagement score snapshots over time."""
    session = models.ForeignKey(
        DeepfaceSession,
        to_field='session_id',
        db_column='session_id',
        on_delete=models.CASCADE,
        related_name='engagement_snapshots',
    )
    timestamp = models.CharField(max_length=50, null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    components = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'deepface_engagement_snapshots'

    def __str__(self):
        return f"Engagement {self.score} @ {self.timestamp}"
