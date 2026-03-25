from .._imports import *


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
        
        if not text.strip() and file_name.endswith('.pdf'):
            # Fallback to OCR for non-selectable PDFs
            from ..ocr_utils import extract_text_from_pdf_ocr
            text = extract_text_from_pdf_ocr(file_content)

        # DEBUG: Log extracted text length
        print(f"DEBUG: Extracted text length: {len(text) if text else 0}")
        if text and len(text) < 100:
             print(f"DEBUG: Extracted text sample: {text[:100]}")

        if not text.strip():
            return Response(
                {'error': 'Could not extract text from the resume file. It might be a scanned document or image-heavy PDF.'},
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
        # Also create a space-stripped version to catch OCR word-splitting artifacts
        # e.g. OCR may read "JavaScript" as "Java Script" -> strip spaces -> "javascript" still matches
        text_nospace = text_lower.replace(" ", "")
        extracted_skills = []

        def _skill_in_text(skill_lower, text_lower, text_nospace):
            """
            Match a skill in text using word boundaries to prevent false positives.
            e.g. 'scala' must NOT match inside 'scalable'.
            Uses negative lookarounds so special-char skills (Node.js, C++) also work.
            """
            escaped = re.escape(skill_lower)
            # Negative lookaround: skill must not be preceded/followed by a-z or 0-9
            if re.search(r'(?<![a-z0-9])' + escaped + r'(?![a-z0-9])', text_lower):
                return True
            # OCR artifact fallback ONLY for multi-word skills:
            # e.g. "JavaScript" (one word) read by OCR as "Java Script" (two words).
            # We only do this for skills that contain a space, so single-word skills
            # like "Scala" are never matched by stripping spaces (prevents 'scala' in 'scalable').
            if ' ' in skill_lower:
                skill_nospace = skill_lower.replace(" ", "")
                if len(skill_nospace) > 4 and skill_nospace in text_nospace:
                    return True
            return False


        # Find skills in the text
        for skill in common_skills:
            if len(skill) <= 2:
                continue
            if skill in extracted_skills:
                continue
            if _skill_in_text(skill.lower(), text_lower, text_nospace):
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


