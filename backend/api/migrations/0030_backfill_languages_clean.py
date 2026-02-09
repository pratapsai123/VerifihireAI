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


def backfill_languages(apps, schema_editor):
    CodingQuestion = apps.get_model("api", "CodingQuestion")
    for q in CodingQuestion.objects.all():
        langs = q.languages or []
        langs_clean = []
        seen = set()
        for v in langs:
            lv = (v or "").strip().lower()
            if lv in DEFAULT_LANGS and lv not in seen:
                langs_clean.append(lv)
                seen.add(lv)
        # If nothing valid, try to seed from primary
        if not langs_clean and q.language:
            lv = q.language.strip().lower()
            if lv in DEFAULT_LANGS:
                langs_clean = [lv]
        q.languages = langs_clean
        q.language = langs_clean[0] if langs_clean else None
        q.save(update_fields=["languages", "language"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0029_set_default_languages_all"),
    ]

    operations = [
        migrations.RunPython(backfill_languages, noop_reverse),
    ]

