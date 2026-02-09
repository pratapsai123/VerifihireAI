from django.db import migrations

DEFAULT_LANGS = [
    "cpp",
    "java",
    "python3",
    "python",
    "javascript",
    "typescript",
    "csharp",
    "c",
    "go",
    "kotlin",
    "swift",
    "rust",
    "ruby",
    "php",
    "dart",
    "scala",
]


def set_languages(apps, schema_editor):
    CodingQuestion = apps.get_model("api", "CodingQuestion")
    for q in CodingQuestion.objects.all():
        q.languages = list(DEFAULT_LANGS)
        if not q.language:
            q.language = DEFAULT_LANGS[0]
        q.save(update_fields=["languages", "language"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0028_backfill_codingquestion_languages"),
    ]

    operations = [
        migrations.RunPython(set_languages, noop_reverse),
    ]

