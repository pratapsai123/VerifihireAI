from django.core.management.base import BaseCommand
from api.models import Question
import random

# All skills from subRoleSkills mapping
ALL_SKILLS = [
    # Programming Languages
    'Java', 'Python', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Ruby', 'PHP',
    'Swift', 'Kotlin', 'Dart', 'Scala', 'R',
    # Frameworks & Libraries
    'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot',
    'Hibernate', 'Node.js', 'Express', 'Laravel', 'Symfony', 'Ruby on Rails',
    # Databases
    'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQL Server', 'Oracle', 'SQLite', 'Redis',
    # Cloud & DevOps
    'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Terraform',
    'Git', 'Linux', 'Microservices',
    # Data & ML
    'Machine Learning', 'Deep Learning', 'Data Analysis', 'Big Data', 'ETL',
    'TensorFlow', 'PyTorch', 'Apache Spark', 'Hadoop',
    # Testing
    'Test Automation', 'Selenium', 'API Testing', 'Performance Testing',
    # Security
    'Application Security', 'Cloud Security', 'Network Security',
    # Other
    'REST API', 'GraphQL', 'System Design', 'Architecture', 'Data Structures',
    'Algorithms', 'Object-Oriented Programming', 'Agile', 'Scrum',
    # Tools
    'Maven', 'Gradle', 'JUnit', 'Pytest', 'Postman', 'Swagger',
    # Frontend
    'HTML', 'CSS', 'Redux', 'Webpack', 'Jest',
    # Backend
    'SQLAlchemy', 'Entity Framework', 'ASP.NET', '.NET',
    # Mobile
    'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin',
    # DevOps Tools
    'Helm', 'Ansible', 'GitLab CI', 'GitHub Actions',
    # Data Tools
    'Apache Airflow', 'Kafka', 'Hive', 'Pig',
    # ML Tools
    'Scikit-learn', 'Keras', 'NLP', 'Computer Vision', 'OpenCV',
    # Analytics
    'Tableau', 'Power BI', 'Excel', 'Statistics',
    # Design
    'UI Design', 'UX Design', 'Figma', 'Adobe XD',
    # Management
    'Product Management', 'Project Management', 'Leadership',
]

# Question templates for different question types
MCQ_TEMPLATES = {
    'easy': [
        "What is the primary purpose of {skill}?",
        "Which of the following is a key feature of {skill}?",
        "What does {skill} primarily help developers with?",
        "In {skill}, what is the most common use case?",
        "Which statement best describes {skill}?",
    ],
    'medium': [
        "How does {skill} handle {concept}?",
        "What is the best practice when using {skill} for {scenario}?",
        "Which approach is recommended for implementing {concept} in {skill}?",
        "What happens when you {action} in {skill}?",
        "How would you optimize {skill} for {scenario}?",
    ],
    'hard': [
        "What are the performance implications of using {skill} in a {scenario}?",
        "How would you architect a {system_type} using {skill}?",
        "What are the trade-offs between {approach1} and {approach2} in {skill}?",
        "How does {skill} handle {complex_scenario} at scale?",
        "What design patterns are most effective when working with {skill}?",
    ]
}

MSQ_TEMPLATES = {
    'easy': [
        "Which of the following are features of {skill}? (Select all that apply)",
        "What are the main benefits of using {skill}? (Select all that apply)",
        "Which statements are true about {skill}? (Select all that apply)",
    ],
    'medium': [
        "Which of the following are best practices when using {skill}? (Select all that apply)",
        "What are the common use cases for {skill}? (Select all that apply)",
        "Which approaches work well with {skill}? (Select all that apply)",
    ],
    'hard': [
        "Which of the following are important considerations when scaling {skill}? (Select all that apply)",
        "What are the key architectural patterns used with {skill}? (Select all that apply)",
        "Which optimization techniques are relevant for {skill}? (Select all that apply)",
    ]
}

TF_TEMPLATES = {
    'easy': [
        "{skill} is primarily used for {purpose}.",
        "{skill} supports {feature}.",
        "{skill} is compatible with {technology}.",
    ],
    'medium': [
        "{skill} requires {requirement} to function properly.",
        "{skill} is the best choice for {scenario}.",
        "When using {skill}, you must always {action}.",
    ],
    'hard': [
        "{skill} can handle {scenario} without performance degradation.",
        "The recommended approach for {skill} in {scenario} is {approach}.",
        "{skill} automatically handles {complex_feature}.",
    ]
}

# Common concepts, scenarios, and options
CONCEPTS = ['error handling', 'memory management', 'concurrency', 'scalability', 'security', 'performance']
SCENARIOS = ['high-traffic applications', 'distributed systems', 'microservices', 'real-time processing', 'large datasets']
ACTIONS = ['initialize', 'configure', 'deploy', 'optimize', 'debug']
SYSTEM_TYPES = ['distributed system', 'microservices architecture', 'event-driven system', 'monolithic application']
APPROACHES = ['synchronous', 'asynchronous', 'reactive', 'imperative', 'declarative']
COMPLEX_SCENARIOS = ['high concurrency', 'low latency', 'fault tolerance', 'data consistency']
PURPOSES = ['web development', 'data processing', 'system integration', 'application development']
FEATURES = ['automatic scaling', 'built-in caching', 'type safety', 'lazy evaluation']
TECHNOLOGIES = ['Docker', 'Kubernetes', 'AWS', 'PostgreSQL', 'Redis']
REQUIREMENTS = ['specific configuration', 'additional dependencies', 'runtime environment']
COMPLEX_FEATURES = ['load balancing', 'failover', 'data replication', 'transaction management']


def generate_mcq_question(skill, difficulty):
    """Generate a Multiple Choice Question"""
    template = random.choice(MCQ_TEMPLATES[difficulty])
    
    # Replace placeholders - provide all possible placeholders
    question_text = template.format(
        skill=skill,
        concept=random.choice(CONCEPTS),
        scenario=random.choice(SCENARIOS),
        action=random.choice(ACTIONS),
        system_type=random.choice(SYSTEM_TYPES),
        approach1=random.choice(APPROACHES),
        approach2=random.choice(APPROACHES),
        complex_scenario=random.choice(COMPLEX_SCENARIOS),
    )
    
    # Generate options
    options = {
        'A': f"Option A: Correct answer related to {skill}",
        'B': f"Option B: Incorrect distractor for {skill}",
        'C': f"Option C: Another incorrect option",
        'D': f"Option D: Common misconception about {skill}",
    }
    
    # Make one option correct (simplified - in production, use AI or predefined answers)
    correct = 'A'
    
    return {
        'question': question_text,
        'option_a': options['A'],
        'option_b': options['B'],
        'option_c': options['C'],
        'option_d': options['D'],
        'correct_answer': correct,
        'question_type': 'MCQ',
    }


def generate_msq_question(skill, difficulty):
    """Generate a Multiple Select Question"""
    template = random.choice(MSQ_TEMPLATES[difficulty])
    
    question_text = template.format(
        skill=skill,
        scenario=random.choice(SCENARIOS),
        concept=random.choice(CONCEPTS),
        action=random.choice(ACTIONS),
    )
    
    options = {
        'A': f"Option A: Feature of {skill}",
        'B': f"Option B: Another feature of {skill}",
        'C': f"Option C: Not related to {skill}",
        'D': f"Option D: Another feature of {skill}",
    }
    
    # Multiple correct answers (A, B, D)
    correct_answers = ['A', 'B', 'D']
    
    return {
        'question': question_text,
        'option_a': options['A'],
        'option_b': options['B'],
        'option_c': options['C'],
        'option_d': options['D'],
        'correct_answers': correct_answers,
        'question_type': 'MSQ',
    }


def generate_tf_question(skill, difficulty):
    """Generate a True/False Question"""
    template = random.choice(TF_TEMPLATES[difficulty])
    
    # Provide all possible placeholders
    question_text = template.format(
        skill=skill,
        purpose=random.choice(PURPOSES),
        feature=random.choice(FEATURES),
        technology=random.choice(TECHNOLOGIES),
        requirement=random.choice(REQUIREMENTS),
        scenario=random.choice(SCENARIOS),
        action=random.choice(ACTIONS),
        approach=random.choice(APPROACHES),
        complex_feature=random.choice(COMPLEX_FEATURES),
        concept=random.choice(CONCEPTS),
        system_type=random.choice(SYSTEM_TYPES),
        complex_scenario=random.choice(COMPLEX_SCENARIOS),
    )
    
    # Randomly assign True or False
    correct_answer = random.choice(['True', 'False'])
    
    return {
        'question': question_text,
        'option_a': 'True',
        'option_b': 'False',
        'correct_answer': correct_answer,
        'question_type': 'TF',
    }


class Command(BaseCommand):
    help = 'Generate 30 questions (10 MCQ, 10 MSQ, 10 TF) for each skill'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skill',
            type=str,
            help='Generate questions for a specific skill only',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of questions per skill (default: 30)',
        )

    def handle(self, *args, **options):
        skills_to_process = [options['skill']] if options['skill'] else ALL_SKILLS
        questions_per_skill = options['count']
        
        total_created = 0
        
        for skill in skills_to_process:
            self.stdout.write(f'Processing skill: {skill}')
            
            # Determine assessment name (simplified - use skill name)
            assessment = skill
            
            # Use skill as topic
            topic = skill
            
            # Generate questions
            questions_created = 0
            
            # Generate MCQ questions (10)
            for i in range(10):
                difficulties = ['easy', 'medium', 'hard']
                difficulty = random.choice(difficulties) if i < 9 else 'hard'
                
                q_data = generate_mcq_question(skill, difficulty)
                Question.objects.create(
                    company_id=None,
                    visibility='GLOBAL',
                    assessment=assessment,
                    topic=topic,
                    question_type=q_data['question_type'],
                    difficulty=difficulty,
                    question=q_data['question'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answer=q_data['correct_answer'],
                )
                questions_created += 1
            
            # Generate MSQ questions (10)
            for i in range(10):
                difficulties = ['easy', 'medium', 'hard']
                difficulty = random.choice(difficulties) if i < 9 else 'hard'
                
                q_data = generate_msq_question(skill, difficulty)
                Question.objects.create(
                    company_id=None,
                    visibility='GLOBAL',
                    assessment=assessment,
                    topic=topic,
                    question_type=q_data['question_type'],
                    difficulty=difficulty,
                    question=q_data['question'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    option_c=q_data['option_c'],
                    option_d=q_data['option_d'],
                    correct_answers=q_data['correct_answers'],
                )
                questions_created += 1
            
            # Generate TF questions (10)
            for i in range(10):
                difficulties = ['easy', 'medium', 'hard']
                difficulty = random.choice(difficulties) if i < 9 else 'hard'
                
                q_data = generate_tf_question(skill, difficulty)
                Question.objects.create(
                    company_id=None,
                    visibility='GLOBAL',
                    assessment=assessment,
                    topic=topic,
                    question_type=q_data['question_type'],
                    difficulty=difficulty,
                    question=q_data['question'],
                    option_a=q_data['option_a'],
                    option_b=q_data['option_b'],
                    correct_answer=q_data['correct_answer'],
                )
                questions_created += 1
            
            total_created += questions_created
            self.stdout.write(
                self.style.SUCCESS(f'Created {questions_created} questions for {skill}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal questions created: {total_created}')
        )

