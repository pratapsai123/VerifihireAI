from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0023_userinvitation"),
    ]

    operations = [
        migrations.CreateModel(
            name="CodingQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("language", models.CharField(choices=[("python", "Python"), ("javascript", "JavaScript")], default="python", max_length=32)),
                ("mode", models.CharField(choices=[("full_program", "Full Program"), ("method_only", "Method Only")], default="full_program", max_length=32)),
                ("template_code", models.TextField(blank=True, null=True)),
                ("starter_code", models.TextField(blank=True, null=True)),
                ("time_limit_ms", models.IntegerField(default=3000)),
                ("memory_limit_mb", models.IntegerField(default=256)),
                ("created_by_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("organization_name_snapshot", models.CharField(blank=True, max_length=255, null=True)),
                ("custom_assessment_id", models.BigIntegerField(blank=True, help_text="Optional link by ID only (no FK)", null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Coding Question",
                "verbose_name_plural": "Coding Questions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CodingSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_id", models.BigIntegerField(db_index=True)),
                ("user_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("candidate_name", models.CharField(blank=True, max_length=255, null=True)),
                ("language", models.CharField(default="python", max_length=32)),
                ("mode", models.CharField(default="full_program", max_length=32)),
                ("submitted_code", models.TextField()),
                ("passed_count", models.IntegerField(default=0)),
                ("total_tests", models.IntegerField(default=0)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("passed", "Passed"),
                            ("failed", "Failed"),
                            ("error", "Error"),
                            ("timeout", "Timeout"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("execution_time_ms", models.IntegerField(blank=True, null=True)),
                ("results", models.JSONField(blank=True, default=dict, help_text="Per-test results snapshot")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Coding Submission",
                "verbose_name_plural": "Coding Submissions",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CodingTestCase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question_id", models.BigIntegerField(db_index=True)),
                ("stdin", models.TextField(blank=True, null=True)),
                ("expected_stdout", models.TextField(blank=True, null=True)),
                ("is_hidden", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Coding Test Case",
                "verbose_name_plural": "Coding Test Cases",
                "ordering": ["question_id", "id"],
            },
        ),
        migrations.AddIndex(
            model_name="codingquestion",
            index=models.Index(fields=["language", "mode"], name="api_codingq_language_5d6c5c_idx"),
        ),
        migrations.AddIndex(
            model_name="codingquestion",
            index=models.Index(fields=["is_active"], name="api_codingq_is_acti_0cbf23_idx"),
        ),
        migrations.AddIndex(
            model_name="codingtestcase",
            index=models.Index(fields=["question_id", "is_hidden"], name="api_codingt_question_0b0db2_idx"),
        ),
        migrations.AddIndex(
            model_name="codingsubmission",
            index=models.Index(fields=["question_id", "status"], name="api_codings_question_8b998f_idx"),
        ),
    ]


