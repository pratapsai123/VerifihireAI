import json
import os
import re
from django.core.management.base import BaseCommand
from api.models import Question, UserProfile

class Command(BaseCommand):
    help = 'Import questions from JSON files to the database'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Import a single JSON file (e.g., Questions/json_format/Android.json)')
        parser.add_argument('--directory', type=str, default='backend/Questions/json_format', 
                          help='Directory with JSON question files (default: backend/Questions/json_format). Ignored if --file is used.')
        parser.add_argument('--assessment', type=str, help='Override assessment name (defaults to filename or skill in JSON)')
        parser.add_argument('--topic', type=str, help='Topic name (defaults to assessment name)')
        parser.add_argument('--type', type=str, default='MCQ', choices=['MCQ', 'MSQ', 'TF'], help='Question type')
        parser.add_argument('--difficulty', type=str, default='auto', choices=['easy', 'medium', 'hard', 'auto'], 
                          help='Difficulty level (auto = analyze based on keywords)')
        parser.add_argument('--time_limit', type=int, default=120, help='Time limit in seconds')
        parser.add_argument('--org_name', type=str, help='Organization name snapshot')
        parser.add_argument('--visibility', type=str, default='COMPANY', choices=['GLOBAL', 'COMPANY', 'PERSONAL'],
                          help='Question visibility level')

    def analyze_difficulty(self, question_text):
        """Simple heuristic to identify difficulty based on keywords."""
        text = question_text.lower()
        
        hard_keys = [
            'architect', 'scale', 'performance', 'trade-off', 'concurrency', 
            'complex', 'optimize', 'distributed', 'security vulnerability',
            'memory leak', 'low-level', 'internal implementation', 'asymptotic'
        ]
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
        name = filename.replace('.json', '')
        if name == 'RubyonRails': return 'Ruby on Rails'
        if name == 'SpringBoot': return 'Spring Boot'
        if name == 'PostgreSQL': return 'PostgreSQL'
        if name == 'ReactNative': return 'React Native'
        
        if not name.isupper():
            name = re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
        
        return name

    def handle(self, *args, **options):
        single_file = options.get('file')
        
        # If single file specified, only process that file
        if single_file:
            if not os.path.exists(single_file):
                self.stderr.write(self.style.ERROR(f"File not found: {single_file}"))
                return
            json_files = [single_file]
        else:
            # Otherwise process entire directory
            directory = options['directory']
            
            if not os.path.exists(directory):
                self.stderr.write(self.style.ERROR(f"Directory not found: {directory}"))
                return

            json_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.json')]
            json_files.sort()

            if not json_files:
                self.stdout.write(self.style.WARNING(f"No JSON files found in {directory}"))
                return

        total_created = 0
        total_skipped = 0

        for file_path in json_files:
            filename = os.path.basename(file_path)
            
            self.stdout.write(f"\n--- Processing: {filename} ---")

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                skill = json_data.get('skill') if isinstance(json_data, dict) else None
                questions_list = json_data.get('questions') if isinstance(json_data, dict) else json_data
                
                if options['assessment']:
                    assessment_name = options['assessment']
                elif skill:
                    assessment_name = skill
                else:
                    assessment_name = self.format_assessment_name(filename)

                topic = options['topic'] or assessment_name
                
                self.stdout.write(f"Assessment: {assessment_name} | Topic: {topic}")

                if not isinstance(questions_list, list):
                    self.stdout.write(self.style.WARNING(f"No questions list found"))
                    continue

                file_count = 0
                skipped = 0
                difficulty_stats = {'easy': 0, 'medium': 0, 'hard': 0}

                for q_data in questions_list:
                    q_text = q_data.get('question', '').strip()
                    if not q_text:
                        continue

                    # IDEMPOTENCY CHECK
                    if Question.objects.filter(assessment=assessment_name, topic=topic, question=q_text).exists():
                        skipped += 1
                        continue

                    # Determine difficulty
                    if options['difficulty'] == 'auto':
                        difficulty = self.analyze_difficulty(q_text)
                    else:
                        difficulty = options['difficulty']
                    
                    opts = q_data.get('options', {})
                    ans = q_data.get('answer')
                    
                    # Initialize answer fields
                    correct_answer = ""
                    correct_answers = []
                    q_type = options['type']
                    
                    is_ans_list = isinstance(ans, list)
                    is_ans_comma_string = isinstance(ans, str) and ',' in ans
                    
                    # Determine question type and answer fields
                    if q_type == 'MSQ' or is_ans_list or is_ans_comma_string:
                        # Multiple Select Question (MSQ)
                        q_type = 'MSQ'
                        if is_ans_list:
                            correct_answers = [str(a).strip() for a in ans]
                        elif isinstance(ans, str):
                            correct_answers = [a.strip() for a in ans.split(',')]
                        elif ans is not None:
                            correct_answers = [str(ans).strip()]
                        correct_answer = ""  # Keep empty for MSQ
                    elif isinstance(ans, str) and ans.lower() in ['true', 'false']:
                        # True/False Question (TF)
                        q_type = 'TF'
                        correct_answer = str(ans).strip()
                        correct_answers = []  # Keep empty for TF
                    else:
                        # Multiple Choice Question (MCQ) - default
                        if q_type != 'TF':
                            q_type = 'MCQ'
                        correct_answer = str(ans).strip() if ans else ""
                        correct_answers = []  # Keep empty for MCQ

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
                        visibility=options['visibility']
                    )
                    file_count += 1
                    difficulty_stats[difficulty] += 1
                
                total_created += file_count
                total_skipped += skipped
                
                self.stdout.write(self.style.SUCCESS(
                    f"[OK] Imported {file_count} | Skipped {skipped} (Easy: {difficulty_stats['easy']}, "
                    f"Medium: {difficulty_stats['medium']}, Hard: {difficulty_stats['hard']})"
                ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f" Error processing {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n Complete! Total imported: {total_created} | Total skipped: {total_skipped}"
        ))

