import json
import os
from django.core.management.base import BaseCommand
from api.models import Question, UserProfile

class Command(BaseCommand):
    help = 'Import objective questions from a JSON file into api_question table'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing questions')
        parser.add_argument('--user_email', type=str, help='Email of the user creating these questions (optional)')
        parser.add_argument('--org_name', type=str, help='Name of the organization (optional)')

    def handle(self, *args, **options):
        json_file_path = options['json_file']
        user_email = options.get('user_email')
        org_name = options.get('org_name')

        if not os.path.exists(json_file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {json_file_path}"))
            return

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                questions_data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error reading JSON file: {e}"))
            return

        if not isinstance(questions_data, list):
            self.stderr.write(self.style.ERROR("JSON data must be a list of questions"))
            return

        user_profile = None
        if user_email:
            try:
                user_profile = UserProfile.objects.get(email=user_email)
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"UserProfile with email {user_email} not found. Questions will be created without a user link."))

        count = 0
        for q_data in questions_data:
            try:
                # Required fields check
                required_fields = ['assessment', 'topic', 'question_type', 'difficulty', 'question']
                missing_fields = [field for field in required_fields if field not in q_data]
                if missing_fields:
                    self.stdout.write(self.style.ERROR(f"Skipping question: missing required fields: {', '.join(missing_fields)}"))
                    continue

                # Create the question
                Question.objects.create(
                    created_by=user_profile,
                    organization_name_snapshot=org_name or q_data.get('organization_name_snapshot'),
                    visibility=q_data.get('visibility', 'GLOBAL'),
                    assessment=q_data['assessment'],
                    topic=q_data['topic'],
                    question_type=q_data['question_type'],
                    difficulty=q_data['difficulty'],
                    question=q_data['question'],
                    option_a=q_data.get('option_a'),
                    option_b=q_data.get('option_b'),
                    option_c=q_data.get('option_c'),
                    option_d=q_data.get('option_d'),
                    correct_answer=q_data.get('correct_answer'),
                    correct_answers=q_data.get('correct_answers', []),
                    time_limit=q_data.get('time_limit', 120),
                )
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating question: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {count} questions."))
