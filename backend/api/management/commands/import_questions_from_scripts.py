import os
import sys
import importlib.util
import re
from django.core.management.base import BaseCommand
from api.models import Question, UserProfile

class Command(BaseCommand):
    help = 'Import questions from PDF generation scripts into the database'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str, help='Path to a single script or a directory containing scripts')
        parser.add_argument('--assessment', type=str, help='Override assessment name (defaults to filename)')
        parser.add_argument('--topic', type=str, help='Topic name (defaults to assessment name)')
        parser.add_argument('--type', type=str, default='MCQ', choices=['MCQ', 'MSQ', 'TF'], help='Question type')
        parser.add_argument('--difficulty', type=str, default='medium', choices=['easy', 'medium', 'hard'], help='Difficulty level')
        parser.add_argument('--time_limit', type=int, default=120, help='Time limit in seconds')
        parser.add_argument('--org_name', type=str, help='Organization name snapshot')

    def analyze_difficulty(self, question_text):
        """Simple heuristic to identify difficulty based on keywords."""
        text = question_text.lower()
        
        # Hard keywords
        hard_keys = [
            'architect', 'scale', 'performance', 'trade-off', 'concurrency', 
            'complex', 'optimize', 'distributed', 'security vulnerability',
            'memory leak', 'low-level', 'internal implementation', 'asymptotic'
        ]
        # Medium keywords
        medium_keys = [
            'how does', 'purpose', 'difference', 'best practice', 'mechanism',
            'logic', 'handle', 'implement', 'validation', 'workflow'
        ]
        
        if any(k in text for k in hard_keys):
            return 'hard'
        if any(k in text for k in medium_keys) or len(text) > 120:
            return 'medium'
        return 'easy'

    def format_assessment_name(self, filename):
        """Formats filename into a readable assessment name."""
        name = filename.replace('.py', '')
        # Handle common camelcase or squashed names
        # e.g., RubyonRails -> Ruby on Rails, Express.js -> Express.js
        if name == 'RubyonRails': return 'Ruby on Rails'
        if name == 'SpringBoot': return 'Spring Boot'
        if name == 'PostgreSQL': return 'PostgreSQL'
        if name == 'ReactNative': return 'React Native'
        
        # Add spaces before capital letters if not all caps
        if not name.isupper():
            name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        
        return name

    def handle(self, *args, **options):
        path = options['path']
        if not os.path.exists(path):
            self.stderr.write(self.style.ERROR(f"Path not found: {path}"))
            return

        files_to_process = []
        if os.path.isfile(path):
            files_to_process.append(path)
        elif os.path.isdir(path):
            for f in os.listdir(path):
                if f.endswith('.py') and f not in ['gen.py', '__init__.py']:
                    files_to_process.append(os.path.join(path, f))

        if not files_to_process:
            self.stdout.write(self.style.WARNING("No valid question scripts found."))
            return

        total_created = 0

        for file_path in files_to_process:
            filename = os.path.basename(file_path)
            
            self.stdout.write(f"\n--- Analyzing & Importing: {filename} ---")

            try:
                # 1. Read the file content to extract the 'skill' variable if it exists at the bottom
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for skill = "SkillName" or skill = 'SkillName'
                skill_match = re.search(r'skill\s*=\s*["\']([^"\']+)["\']', content)
                
                # 2. Smart Analysis of Assessment Name
                if options['assessment']:
                    assessment_name = options['assessment']
                elif skill_match:
                    assessment_name = skill_match.group(1)
                else:
                    assessment_name = self.format_assessment_name(filename)

                topic = options['topic'] or assessment_name
                
                self.stdout.write(f"Detected Assessment: {assessment_name}")

                spec = importlib.util.spec_from_file_location("question_script", file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, 'QUESTIONS'):
                    continue

                questions_list = module.QUESTIONS
                if not isinstance(questions_list, list):
                    continue

                seen_texts = set()
                file_count = 0
                difficulty_stats = {'easy': 0, 'medium': 0, 'hard': 0}

                for q_data in questions_list:
                    q_text = q_data.get('question', '').strip()
                    if not q_text or q_text in seen_texts:
                        continue
                    
                    seen_texts.add(q_text)

                    # IDEMPOTENCY CHECK: Skip if this specific question already exists in DB
                    if Question.objects.filter(assessment=assessment_name, topic=topic, question=q_text).exists():
                        continue

                    # Smart Analysis of Difficulty
                    # If the user didn't force a difficulty in command line, we analyze it
                    difficulty = options['difficulty'] if options['difficulty'] != 'medium' else self.analyze_difficulty(q_text)
                    
                    opts = q_data.get('options', {})
                    
                    # Handle potential MSQ (multiple answers)
                    ans = q_data.get('answer')
                    correct_answer = ""
                    correct_answers = []
                    
                    if isinstance(ans, list):
                        correct_answers = ans
                        q_type = 'MSQ'
                    else:
                        correct_answer = str(ans)
                        q_type = options['type']
                        if correct_answer.lower() in ['true', 'false']:
                            q_type = 'TF'

                    Question.objects.create(
                        assessment=assessment_name,
                        topic=topic,
                        question_type=q_type,
                        difficulty=difficulty,
                        time_limit=options['time_limit'],
                        question=q_text,
                        option_a=opts.get('A'),
                        option_b=opts.get('B'),
                        option_c=opts.get('C'),
                        option_d=opts.get('D'),
                        correct_answer=correct_answer,
                        correct_answers=correct_answers,
                        organization_name_snapshot=options['org_name'],
                        visibility='COMPANY'
                    )
                    file_count += 1
                    difficulty_stats[difficulty] += 1
                
                total_created += file_count
                self.stdout.write(self.style.SUCCESS(
                    f"Done! Imported {file_count} questions: "
                    f"Easy: {difficulty_stats['easy']}, Medium: {difficulty_stats['medium']}, Hard: {difficulty_stats['hard']}"
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"\nTotal questions imported: {total_created}"))
