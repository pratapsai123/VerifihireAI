from ._imports import *


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def extract_skills_from_resume_view(request):
    """
    Extract skills from uploaded resume file.
    Expected request: multipart/form-data with 'resume' file field
    Supports: PDF, DOC, DOCX files
    """
    try:
        if 'resume' not in request.FILES:
            return Response(
                {'error': 'No resume file provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resume_file = request.FILES['resume']
        file_name = resume_file.name.lower()
        
        # Validate file type
        if not (file_name.endswith('.pdf') or file_name.endswith('.doc') or file_name.endswith('.docx')):
            return Response(
                {'error': 'Invalid file type. Please upload PDF, DOC, or DOCX file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Read file content
        file_content = resume_file.read()
        
        # Extract text based on file type
        text = ""
        try:
            if file_name.endswith('.pdf'):
                # Extract text from PDF
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    text += page.extract_text() + " "
            elif file_name.endswith('.docx'):
                # Extract text from DOCX
                doc = Document(io.BytesIO(file_content))
                for paragraph in doc.paragraphs:
                    text += paragraph.text + " "
                # Also extract text from tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            text += cell.text + " "
            elif file_name.endswith('.doc'):
                # DOC files require additional libraries (python-docx doesn't support .doc)
                # For now, return an error or use a workaround
                return Response(
                    {'error': 'DOC files are not fully supported. Please convert to PDF or DOCX.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            return Response(
                {'error': f'Error reading file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not text.strip():
            return Response(
                {'error': 'Could not extract text from the resume file.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract skills from text
        # Common technical skills database
        common_skills = [
            # Programming Languages
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'C', 'Go', 'Rust', 'Swift', 'Kotlin',
            'PHP', 'Ruby', 'Perl', 'Scala', 'R', 'MATLAB', 'Dart', 'Lua', 'Shell', 'Bash',
            # Web Technologies
            'HTML', 'CSS', 'HTML5', 'CSS3', 'React', 'Angular', 'Vue', 'Vue.js', 'Node.js', 'Express',
            'Django', 'Flask', 'FastAPI', 'Spring', 'Spring Boot', 'ASP.NET', 'Laravel', 'Symfony',
            'jQuery', 'Bootstrap', 'Tailwind CSS', 'SASS', 'SCSS', 'Less',
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle', 'SQLite', 'Cassandra',
            'DynamoDB', 'Elasticsearch', 'Neo4j', 'Firebase', 'MariaDB',
            # Cloud & DevOps
            'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD',
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'Terraform', 'Ansible', 'Chef', 'Puppet',
            'Linux', 'Unix', 'Windows', 'Ubuntu', 'CentOS',
            # Mobile Development
            'iOS', 'Android', 'React Native', 'Flutter', 'Xamarin', 'Ionic',
            # Data Science & AI
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Keras', 'Scikit-learn',
            'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Data Analysis',
            # Other Technologies
            'REST API', 'GraphQL', 'Microservices', 'Agile', 'Scrum', 'DevOps',
            'Blockchain', 'Ethereum', 'Solidity', 'Web3',
            'GraphQL', 'gRPC', 'RabbitMQ', 'Kafka', 'Apache', 'Nginx',
            # Tools & Frameworks
            'Jira', 'Confluence', 'Slack', 'Trello', 'Asana', 'Postman', 'Swagger',
            'Webpack', 'Babel', 'ESLint', 'Prettier', 'Jest', 'Mocha', 'Cypress',
            'Selenium', 'Playwright', 'Pytest', 'Unit Testing', 'Integration Testing',
        ]
        
        # Normalize text for matching (case-insensitive)
        text_lower = text.lower()
        extracted_skills = []
        
        # Find skills in the text
        for skill in common_skills:
            # Check if skill appears in text (case-insensitive, whole word or as part of a phrase)
            skill_lower = skill.lower()
            # Match whole word or as part of common phrases
            if skill_lower in text_lower:
                # Avoid duplicates and very short matches
                if skill not in extracted_skills and len(skill) > 2:
                    extracted_skills.append(skill)
        
        # Sort skills alphabetically
        extracted_skills.sort()
        
        return Response(
            {
                'skills': extracted_skills,
                'count': len(extracted_skills),
                'message': f'Successfully extracted {len(extracted_skills)} skills from resume.'
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in extract_skills_from_resume_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while extracting skills: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


