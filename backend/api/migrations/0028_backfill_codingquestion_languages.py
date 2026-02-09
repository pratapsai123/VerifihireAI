from django.db import migrations


def backfill_languages(apps, schema_editor):
    CodingQuestion = apps.get_model("api", "CodingQuestion")
    for q in CodingQuestion.objects.all():
        # If languages is empty or None, seed with primary language
        if not q.languages:
            q.languages = [q.language] if q.language else []
            q.save(update_fields=["languages"])


def noop_reverse(apps, schema_editor):
    # No-op reverse; safe to leave languages as-is
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0027_codingquestion_languages"),
    ]

    operations = [
        migrations.RunPython(backfill_languages, noop_reverse),
    ]

