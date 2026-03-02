from ._imports import *



@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_questions_view(request):
    """
    Get questions based on topic, assessment, or skill filters.
    Query parameters:
    - topic: Filter by topic (skill name)
    - assessment: Filter by assessment name
    - question_type: Filter by type (MCQ, MSQ, TF)
    - difficulty: Filter by difficulty (easy, medium, hard)
    - limit: Limit number of results
    - visibility: Filter by visibility (default: GLOBAL)
    """
    try:
        topic = request.GET.get('topic', '').strip()
        assessment = request.GET.get('assessment', '').strip()
        question_type = request.GET.get('question_type', '').strip()
        difficulty = request.GET.get('difficulty', '').strip()
        limit = request.GET.get('limit', None)
        visibility = request.GET.get('visibility', 'GLOBAL').strip()
        
        # Start with all GLOBAL questions
        questions = Question.objects.filter(visibility='GLOBAL', company_id__isnull=True)
        
        # Apply filters
        if topic:
            questions = questions.filter(topic__icontains=topic)
        
        if assessment:
            questions = questions.filter(assessment__icontains=assessment)
        
        if question_type:
            questions = questions.filter(question_type=question_type.upper())
        
        if difficulty:
            questions = questions.filter(difficulty=difficulty.lower())
        
        # Apply limit
        if limit:
            try:
                limit = int(limit)
                questions = questions[:limit]
            except ValueError:
                pass
        
        # Serialize questions
        questions_list = []
        for q in questions:
            question_data = {
                'id': q.id,
                'assessment': q.assessment,
                'topic': q.topic,
                'question_type': q.question_type,
                'difficulty': q.difficulty,
                'question': q.question,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_answer': q.correct_answer,
                'correct_answers': q.correct_answers if q.correct_answers else [],
                'time_limit': q.time_limit,
                'created_at': q.created_at.isoformat() if q.created_at else None,
            }
            questions_list.append(question_data)
        
        return Response(
            {
                'count': len(questions_list),
                'results': questions_list,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _parse_mmss_to_seconds(value: Optional[str]) -> Optional[int]:
    """
    Parse a string like 'mm:ss' into seconds.
    Returns None if value is falsy or cannot be parsed.
    """
    if not value:
        return None
    try:
        text = str(value).strip()
        if not text:
            return None
        if ':' not in text:
            # allow plain seconds
            seconds = int(text)
            return max(0, seconds)
        mm, ss = text.split(':', 1)
        minutes = int(mm) if mm else 0
        seconds = int(ss) if ss else 0
        if seconds < 0:
            seconds = 0
        if seconds > 59:
            seconds = 59
        total = minutes * 60 + seconds
        # cap to 99:59 to match frontend mm:ss UI
        return min(total, 99 * 60 + 59)
    except Exception:
        return None


def _difficulty_from_experience_level(experience_level: Optional[str]) -> str:
    """
    Map frontend experience levels to Question.difficulty choices.
    """
    level = (experience_level or '').strip().lower()
    mapping = {
        'entry': 'easy',
        'mid': 'medium',
        'senior': 'hard',
        'expert': 'hard',
    }
    return mapping.get(level, 'easy')


def _create_question_from_payload(
    data: dict,
    *,
    preloaded_custom_assessment: Optional["CustomAssessment"] = None,
    preloaded_created_by: Optional["UserProfile"] = None,
    preloaded_company: Optional["Company"] = None,
) -> "Question":
    """
    Internal helper to create a Question from a payload dict.
    Raises ValueError for validation issues.
    """
    data = data or {}

    custom_assessment_id = data.get('custom_assessment_id', None)
    user_email = (data.get('user_email') or data.get('email') or '').strip().lower() or None
    org_name_from_client = (data.get('organization_name') or data.get('company_name') or '').strip() or None
    assessment = (data.get('assessment') or '').strip() or 'Manual'
    topic = (data.get('topic') or '').strip()
    question_type = (data.get('question_type') or '').strip().upper()
    question_text = (data.get('question') or '').strip()

    if not topic:
        topic = 'General'
        print(f"DEBUG: Missing topic in payload, defaulting to '{topic}'")

    if question_type not in ('MCQ', 'MSQ', 'TF'):
        # Try to infer or default
        question_type = 'MCQ'
        print(f"DEBUG: Invalid question_type in payload, defaulting to '{question_type}'")

    if not question_text:
        print("DEBUG: Missing question text in payload.")
        raise ValueError('question is required.')

    option_a = (data.get('option_a') or '').strip() or None
    option_b = (data.get('option_b') or '').strip() or None
    option_c = (data.get('option_c') or '').strip() or None
    option_d = (data.get('option_d') or '').strip() or None

    # For TF, default options are True/False if not provided
    if question_type == 'TF':
        option_a = option_a or 'True'
        option_b = option_b or 'False'

    if not option_a:
        option_a = 'Option A'
        print("DEBUG: Missing option_a, defaulting.")
    if not option_b:
        option_b = 'Option B'
        print("DEBUG: Missing option_b, defaulting.")

    difficulty = (data.get('difficulty') or '').strip().lower()
    if difficulty not in ('easy', 'medium', 'hard'):
        difficulty = _difficulty_from_experience_level(data.get('experience_level'))

    time_limit = data.get('time_limit', None)
    if time_limit is not None:
        try:
            time_limit = int(time_limit)
        except (TypeError, ValueError):
            time_limit = None
    if time_limit is None:
        time_limit = _parse_mmss_to_seconds(data.get('time_to_answer')) or 120

    correct_answer = (data.get('correct_answer') or '').strip().upper() or None
    correct_answers = data.get('correct_answers', None)
    if correct_answers is None:
        correct_answers = []
    if not isinstance(correct_answers, list):
        correct_answers = []
    correct_answers = [str(x).strip().upper() for x in correct_answers if str(x).strip()]

    if question_type == 'MCQ':
        if correct_answer not in ('A', 'B', 'C', 'D'):
            raise ValueError('correct_answer must be one of A, B, C, D for MCQ.')
        correct_answers = []
    elif question_type == 'TF':
        if correct_answer not in ('A', 'B'):
            raise ValueError('correct_answer must be A (True) or B (False) for TF.')
        correct_answers = []
        option_c = None
        option_d = None
    else:  # MSQ
        allowed = {'A', 'B', 'C', 'D'}
        correct_answers = [x for x in correct_answers if x in allowed]
        correct_answers = list(dict.fromkeys(correct_answers))  # unique preserve order
        if len(correct_answers) == 0:
            raise ValueError('correct_answers must be a non-empty array for MSQ.')
        correct_answer = None

    # Link manual questions to CustomAssessment (separate from company_id)
    custom_assessment = preloaded_custom_assessment
    if custom_assessment is None and custom_assessment_id is not None:
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            raise ValueError('custom_assessment_id must be an integer.')
        try:
            custom_assessment = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            raise ValueError(
                f'Custom assessment ID {caid} was not found. Please go back to Review page and recreate the assessment.'
            )

    created_by = preloaded_created_by
    if created_by is None and user_email:
        try:
            created_by = UserProfile.objects.get(email=user_email)
        except UserProfile.DoesNotExist:
            created_by = None

    # company_id should represent the logged-in company, not the customAssessmentId.
    company_id = None
    visibility = 'GLOBAL'
    org_name = (created_by.organization_name if created_by else None) or org_name_from_client or None
    company = preloaded_company
    if org_name and company is None:
        company, _ = _db_call_with_retry(lambda: Company.objects.get_or_create(name=org_name), retries=1)
    if company:
        company_id = company.id
        visibility = 'COMPANY'

    q = _db_call_with_retry(
        lambda: Question.objects.create(
            created_by=created_by,
            organization_name_snapshot=(org_name or (created_by.organization_name if created_by else None)),
            custom_assessment=custom_assessment,
            company_id=company_id,
            visibility=visibility,
            assessment=assessment,
            topic=topic,
            question_type=question_type,
            difficulty=difficulty,
            question=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer,
            correct_answers=correct_answers,
            time_limit=time_limit,
        ),
        retries=1,
    )
    return q


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_question_view(request):
    """
    Create a manual Question (MCQ/MSQ/TF) from the Manual Questions UI.

    Expected request body (JSON):
    {
      "custom_assessment_id": 123,              // optional, used to group "manual" questions
      "assessment": "React Developer",          // optional (defaults to "Manual")
      "topic": "React Hooks",                   // required
      "question_type": "MCQ" | "MSQ" | "TF",    // required
      "difficulty": "easy"|"medium"|"hard",     // optional
      "experience_level": "entry|mid|senior|expert", // optional alternative to difficulty
      "question": "....",                       // required
      "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...", // required for A/B, optional for C/D
      "correct_answer": "A",                    // required for MCQ/TF (TF: A=True, B=False)
      "correct_answers": ["A","C"],             // required for MSQ
      "time_limit": 90,                         // optional seconds
      "time_to_answer": "01:30"                 // optional mm:ss (alternative)
    }
    """
    try:
        data = request.data or {}
        try:
            print(f"Incoming payload for create_question_view: {data}")
            q = _create_question_from_payload(data)
            print(f"Successfully created question ID: {q.id} for custom_assessment_id: {data.get('custom_assessment_id')}")
        except ValueError as ve:
            print(f"Validation error in create_question_view: {str(ve)}")
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                'message': 'Question created successfully.',
                'id': q.id,
                'question': {
                    'id': q.id,
                    'company_name': (q.organization_name_snapshot or (q.created_by.organization_name if q.created_by else None)),
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                },
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError:
        # DB unreachable (common when Supabase host/port blocked or VPN/internet down)
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating question. '
                    'Please check your internet/VPN and that the DB host/port (5432) is reachable, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_question_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating question: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_manual_questions_view(request):
    """
    Fetch manual questions created for a given custom_assessment_id.
    Query params:
    - custom_assessment_id: required
    """
    try:
        custom_assessment_id = request.GET.get('custom_assessment_id', None)
        if custom_assessment_id is None or str(custom_assessment_id).strip() == '':
            return Response({'error': 'custom_assessment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = (
            Question.objects.filter(custom_assessment_id=caid)
            .select_related('created_by', 'custom_assessment')
            .order_by('created_at')
        )
        q_list = _db_call_with_retry(lambda: list(qs), retries=1)

        # Also fetch CodingQuestions for this custom_assessment_id
        coding_qs = CodingQuestion.objects.filter(custom_assessment_id=caid).order_by('created_at')
        coding_list = _db_call_with_retry(lambda: list(coding_qs), retries=1)

        results = []
        # Add regular questions
        for q in q_list:
            results.append(
                {
                    'id': q.id,
                    'company_name': (q.organization_name_snapshot or (q.created_by.organization_name if q.created_by else None)),
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                }
            )

        # Add coding questions
        for cq in coding_list:
            results.append(
                {
                    'id': cq.id,
                    'company_name': cq.organization_name_snapshot,
                    'assessment': 'Coding Challenge',
                    'topic': 'Coding', # This ensures it groups under "Coding" or similar if needed
                    'question_type': 'CODING',
                    'difficulty': cq.difficulty,
                    'question': cq.title, # Title is the main identifier
                    'title': cq.title,
                    'description': cq.description,
                    'language': cq.language,
                    'languages': cq.languages,
                    'mode': cq.mode,
                    'starter_code': cq.starter_code,
                    'schema_sql': cq.schema_sql,
                    'database_engine': cq.database_engine,
                    'time_limit_ms': cq.time_limit_ms,
                    'memory_limit_mb': cq.memory_limit_mb,
                    'created_at': cq.created_at.isoformat() if cq.created_at else None,
                }
            )

        # Sort combined results by created_at
        results.sort(key=lambda x: x.get('created_at') or '', reverse=False)

        return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while fetching manual questions. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in get_manual_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching manual questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _extract_text_from_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    Return (text, filename). Supports PDF, DOCX, TXT.
    """
    filename = getattr(uploaded_file, 'name', 'upload').lower()
    content = uploaded_file.read()
    text = ""
    if filename.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += (page.extract_text() or '') + "\n"
    elif filename.endswith('.doc'):
        # Legacy .doc (binary) is not supported by python-docx; require DOCX.
        raise ValueError('DOC files are not supported. Please convert the Word file to .docx and upload again.')
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(content))
        # Paragraphs (includes most body text, lists, etc.)
        for p in doc.paragraphs:
            text += (p.text or '') + "\n"
        # Tables (Word docs often store content inside tables; python-docx won't include these in paragraphs)
        try:
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = (cell.text or '').strip()
                        if cell_text:
                            text += cell_text + "\n"
        except Exception:
            # If tables are malformed, still return paragraph text.
            pass
    else:
        # fallback: treat as UTF-8 text
        try:
            text = content.decode('utf-8', errors='ignore')
        except Exception:
            text = str(content)
    return text, filename


def _normalize_lines(text: str) -> list[str]:
    lines = (text or '').replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return [ln.strip() for ln in lines if ln.strip()]


def _parse_question_blocks(lines: list[str]) -> list[list[str]]:
    """
    Split into blocks by Q markers; fallback to blank-line style already removed, so heuristic.
    """
    blocks: list[list[str]] = []
    current: list[str] = []
    started = False
    for ln in lines:
        # Start a new block if it looks like "Q1." or "1)" etc.
        if re.match(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', ln, re.IGNORECASE):
            started = True
            if current:
                blocks.append(current)
            current = [ln]
        else:
            # Ignore any preamble/header text before the first question marker
            if not started:
                continue
            current.append(ln)
    if current:
        blocks.append(current)
    # If it didn't split well (single huge block), try to split by "Answer:" occurrences
    if len(blocks) <= 1:
        blocks = []
        current = []
        for ln in lines:
            # Ignore any preamble/header text before the first question marker
            if not started and not re.match(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', ln, re.IGNORECASE):
                continue
            started = True
            current.append(ln)
            # Word/PDF extraction sometimes puts "Answer:" mid-line; treat that as a block terminator too.
            if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
                blocks.append(current)
                current = []
        if current:
            blocks.append(current)
    return [b for b in blocks if any(b)]


def _parse_single_block(block: list[str], defaults: dict) -> tuple[Optional[dict], list[str]]:
    """
    Parse one question block into our schema.
    Returns (question_dict or None, warnings)
    """
    warnings: list[str] = []
    text_lines = [ln.strip() for ln in block if ln.strip()]
    if not text_lines:
        return None, warnings

    raw = " ".join(text_lines)

    # Detect explicit type (only from explicit MCQ/MSQ/TF markers, not from words in a sentence)
    qtype = None
    for ln in text_lines[:3]:
        m = re.search(r'\b(MCQ|MSQ|TF)\b', ln, re.IGNORECASE)
        if m:
            qtype = m.group(1).upper()
            break

    # Parse options (allow optional leading bullets like "• A)" or "- A)")
    opt_re = re.compile(r'^[\s\-\*\u2022]*?(A|B|C|D)\s*[\).:\-]\s*(.+)$', re.IGNORECASE)
    options = {}
    for ln in text_lines:
        m = opt_re.match(ln)
        if m:
            options[m.group(1).upper()] = m.group(2).strip()

    # Parse answer line
    ans_line = None
    for ln in text_lines[::-1]:
        # "Answer:" may appear mid-line depending on extraction; detect anywhere in the line.
        if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
            ans_line = ln
            break
    correct_answer = None
    correct_answers: list[str] = []
    tf_answer_word = False
    if ans_line:
        # Extract the substring after the first "Answer:"/"Correct answer:" marker
        m = re.search(r'(?:answer|correct(?:\s*answer)?)\s*[:\-]\s*(.+)$', ans_line, re.IGNORECASE)
        val = (m.group(1).strip() if m else '').strip()
        # Normalize for TF words
        if re.match(r'^(true|false)\b', val, re.IGNORECASE):
            tf_answer_word = True
            correct_answer = 'A' if val.lower().startswith('true') else 'B'
        else:
            letters = re.findall(r'[ABCD]', val.upper())
            if letters:
                if len(set(letters)) > 1:
                    correct_answers = list(dict.fromkeys(letters))
                else:
                    correct_answer = letters[0]

    # If options weren't detected line-by-line, attempt to extract inline options from the full block text.
    # This handles PDFs where options are emitted on the same line like: "A) ... B) ... C) ... D) ..."
    if not options:
        raw_for_options = raw
        if ans_line:
            # Remove the answer line to avoid confusing option extraction in edge cases
            raw_for_options = raw_for_options.replace(ans_line, ' ')
        opt_marker = re.compile(r'\b([ABCD])\s*[\).:\-]\s*', re.IGNORECASE)
        matches = list(opt_marker.finditer(raw_for_options))
        if matches:
            for idx, m in enumerate(matches):
                key = m.group(1).upper()
                start = m.end()
                end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_for_options)
                value = raw_for_options[start:end].strip()
                # Trim any trailing "Answer:" text that might appear in the same chunk (often mid-line)
                value = re.split(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', value, maxsplit=1, flags=re.IGNORECASE)[0].strip()
                if value:
                    options[key] = value

    # Infer type if missing
    if not qtype:
        if tf_answer_word:
            qtype = 'TF'
        elif options.get('A', '').lower() in ('true', 'false') and options.get('B', '').lower() in ('true', 'false'):
            qtype = 'TF'
        elif correct_answers:
            qtype = 'MSQ'
        else:
            qtype = 'MCQ'

    # Parse question text: take first non-metadata line, strip Q prefix and type tokens.
    # If "Answer:" is on the SAME LINE as the question (common in DOCX), use the part before "Answer:".
    q_text = None
    for ln in text_lines:
        if opt_re.match(ln):
            continue
        if re.search(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, re.IGNORECASE):
            # Example: "26. JVM is platform dependent. Answer: True"
            # Keep left side as the question text candidate.
            left = re.split(r'\b(?:answer|correct(?:\s*answer)?)\s*[:\-]', ln, maxsplit=1, flags=re.IGNORECASE)[0].strip()
            if not left:
                continue
            ln = left
        # Remove leading "Q1." etc
        cleaned = re.sub(r'^(?:q(?:uestion)?\s*)?\d+[\).:\-]\s*', '', ln, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r'\b(MCQ|MSQ|TF)\b', '', cleaned, flags=re.IGNORECASE).strip(' :-')
        if cleaned:
            q_text = cleaned
            break

    if not q_text:
        warnings.append('Could not detect question text.')
        return None, warnings

    # Ensure required options
    if qtype == 'TF':
        option_a = 'True'
        option_b = 'False'
        option_c = None
        option_d = None
        if correct_answer not in ('A', 'B'):
            warnings.append('TF question missing valid answer; defaulting to A.')
            correct_answer = 'A'
    else:
        option_a = options.get('A')
        option_b = options.get('B')
        option_c = options.get('C')
        option_d = options.get('D')
        if not option_a or not option_b:
            warnings.append('Missing option A or B.')
        if qtype == 'MCQ':
            if correct_answer not in ('A', 'B', 'C', 'D'):
                warnings.append('MCQ missing correct_answer.')
        else:  # MSQ
            if not correct_answers:
                warnings.append('MSQ missing correct_answers.')

    # Optional time parsing e.g. "Time: 01:30"
    time_to_answer = defaults.get('time_to_answer') or None
    for ln in text_lines:
        tm = re.match(r'^(?:time|time\s*limit)\s*[:\-]\s*(.+)$', ln, re.IGNORECASE)
        if tm:
            time_to_answer = tm.group(1).strip()
            break

    return (
        {
            'assessment': defaults.get('assessment') or 'Manual',
            'topic': defaults.get('topic') or '',
            'question_type': qtype,
            'question': q_text,
            'option_a': option_a,
            'option_b': option_b,
            'option_c': option_c,
            'option_d': option_d,
            'correct_answer': correct_answer,
            'correct_answers': correct_answers,
            'time_to_answer': time_to_answer,
        },
        warnings,
    )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def parse_questions_document_view(request):
    """
    Parse uploaded PDF/DOCX into question objects.
    multipart/form-data:
      - file: required
      - assessment: optional
      - topic: optional (default topic if PDF doesn't include)
      - experience_level: optional (not used in parsing; passed to save step)
    """
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'file is required.'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        assessment = (request.data.get('assessment') or '').strip() or 'Manual'
        topic = (request.data.get('topic') or '').strip() or ''
        time_to_answer = (request.data.get('time_to_answer') or '').strip() or None

        try:
            text, filename = _extract_text_from_uploaded_file(uploaded_file)
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        lines = _normalize_lines(text)
        if not lines:
            return Response({'error': 'No text could be extracted from the document.'}, status=status.HTTP_400_BAD_REQUEST)

        blocks = _parse_question_blocks(lines)
        defaults = {'assessment': assessment, 'topic': topic, 'time_to_answer': time_to_answer}

        questions: list[dict] = []
        errors: list[str] = []
        for i, block in enumerate(blocks, start=1):
            q, warns = _parse_single_block(block, defaults)
            if q:
                questions.append(q)
                for w in warns:
                    errors.append(f"Q{i}: {w}")
            else:
                errors.append(f"Q{i}: Could not parse this block.")

        return Response({'filename': filename, 'count': len(questions), 'questions': questions, 'errors': errors}, status=status.HTTP_200_OK)

    except Exception as e:
        import traceback
        print(f"Error in parse_questions_document_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while parsing: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def bulk_create_questions_view(request):
    """
    Bulk create questions in DB.
    JSON body:
    {
      "custom_assessment_id": 123,
      "user_email": "...",
      "organization_name": "...",
      "questions": [ {question payload compatible with create_question_view}, ... ]
    }
    """
    try:
        data = request.data or {}
        custom_assessment_id = data.get('custom_assessment_id', None)
        print(f"bulk_create_questions_view: custom_assessment_id={custom_assessment_id}")
        user_email = data.get('user_email', None)
        organization_name = data.get('organization_name', None)
        questions = data.get('questions', [])

        if not custom_assessment_id:
            return Response({'error': 'custom_assessment_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(questions, list) or len(questions) == 0:
            return Response({'error': 'questions must be a non-empty array.'}, status=status.HTTP_400_BAD_REQUEST)

        # Preload shared context to avoid N queries for each question
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            custom_assessment = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            return Response(
                {'error': f'Custom assessment ID {caid} was not found. Please go back to Review page and recreate the assessment.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_by = None
        resolved_user_email = (user_email or '').strip().lower() or None
        if resolved_user_email:
            try:
                created_by = UserProfile.objects.get(email=resolved_user_email)
            except UserProfile.DoesNotExist:
                created_by = None

        company = None
        resolved_org = (organization_name or '').strip() or None
        if resolved_org:
            company, _ = Company.objects.get_or_create(name=resolved_org)

        created_ids = []
        errors = []

        for idx, q in enumerate(questions, start=1):
            try:
                payload = dict(q or {})
                payload['custom_assessment_id'] = custom_assessment_id
                if user_email:
                    payload['user_email'] = user_email
                if organization_name:
                    payload['organization_name'] = organization_name

                created = _create_question_from_payload(
                    payload,
                    preloaded_custom_assessment=custom_assessment,
                    preloaded_created_by=created_by,
                    preloaded_company=company,
                )
                created_ids.append(created.id)
            except Exception as e:
                import traceback
                error_msg = f"Q{idx}: {str(e)}"
                print(f"Error in bulk_create_questions_view during question {idx} creation: {error_msg}")
                # print(traceback.format_exc())
                errors.append(error_msg)

        return Response(
            {
                'created_count': len([x for x in created_ids if x]),
                'created_ids': [x for x in created_ids if x],
                'errors': errors,
            },
            status=status.HTTP_201_CREATED if len(errors) == 0 else status.HTTP_207_MULTI_STATUS
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while bulk creating questions. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in bulk_create_questions_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while bulk creating: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_questions_by_skills_view(request):
    """
    Get questions for multiple skills/topics.
    Query parameters:
    - skills: Comma-separated list of skills
    - limit_per_skill: Number of questions per skill (default: all available)
    - question_type: Filter by type (optional)
    - difficulty: Filter by difficulty (optional)
    """
    try:
        skills_param = request.GET.get('skills', '').strip()
        limit_per_skill = request.GET.get('limit_per_skill', None)
        question_type = request.GET.get('question_type', '').strip()
        difficulty = request.GET.get('difficulty', '').strip()
        
        if not skills_param:
            return Response(
                {'error': 'Skills parameter is required. Provide comma-separated list of skills.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        skills = [s.strip() for s in skills_param.split(',') if s.strip()]
        
        if not skills:
            return Response(
                {'error': 'No valid skills provided.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get questions for each skill
        questions_by_topic = {}
        total_count = 0
        
        for skill in skills:
            # Try exact match first, then case-insensitive contains
            questions = Question.objects.filter(
                visibility='GLOBAL',
                company_id__isnull=True
            ).filter(
                models.Q(topic__iexact=skill) | models.Q(topic__icontains=skill)
            )
            
            if question_type:
                questions = questions.filter(question_type=question_type.upper())
            
            if difficulty:
                questions = questions.filter(difficulty=difficulty.lower())
            
            # Order by created_at for consistent results
            questions = questions.order_by('created_at')
            
            if limit_per_skill:
                try:
                    limit = int(limit_per_skill)
                    questions = questions[:limit]
                except ValueError:
                    pass
            
            # Serialize questions
            questions_list = []
            for q in questions:
                question_data = {
                    'id': q.id,
                    'assessment': q.assessment,
                    'topic': q.topic,
                    'question_type': q.question_type,
                    'difficulty': q.difficulty,
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'correct_answers': q.correct_answers if q.correct_answers else [],
                    'time_limit': q.time_limit,
                    'created_at': q.created_at.isoformat() if q.created_at else None,
                }
                questions_list.append(question_data)
            
            questions_by_topic[skill] = questions_list
            total_count += len(questions_list)
        
        return Response(
            {
                'count': total_count,
                'skills': skills,
                'questions_by_topic': questions_by_topic,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        import traceback
        print(f"Error in get_questions_by_skills_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching questions: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_custom_assessment_view(request):
    """
    Create and store a CustomAssessment record with all configuration data
    coming from the CustomAssessment page on the frontend.

    Expected request body (JSON):
    {
        "user": {
            "first_name": "...",
            "last_name": "...",
            "email": "...",
            "organization_name": "..."
        },
        "assessment": {
            "role": "...",
            "sub_roles": [...],
            "custom_role": "...",
            "experience_level": "entry|mid|senior|expert",
            "number_of_questions": 10,
            "time": "01:20:00",
            "auto_time": "01:20:00",
            "weights": {
                "common": 70,
                "role": 15,
                "resume": 15
            },
            "question_distribution": { "Python": 3, "Django": 2 },
            "removed_skills": [...],
            "extracted_skills": [...],
            "suggested_skills": [...],
            "common_skills": [...],
            "resume_file_name": "candidate_resume.pdf"
        }
    }
    """
    try:
        user_data = request.data.get('user', {}) or {}
        assessment_data = request.data.get('assessment', {}) or {}

        # Basic required fields validation
        role = assessment_data.get('role', '').strip()
        number_of_questions = assessment_data.get('number_of_questions', None)
        time_value = assessment_data.get('time', '').strip()

        if not role:
            return Response(
                {'error': 'role is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            number_of_questions = int(number_of_questions)
        except (TypeError, ValueError):
            return Response(
                {'error': 'number_of_questions must be an integer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if number_of_questions < 1:
            return Response(
                {'error': 'number_of_questions must be at least 1.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not time_value:
            return Response(
                {'error': 'time is required (HH:MM:SS).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find linked UserProfile if possible (by email)
        email = (user_data.get('email') or '').strip().lower() or None
        user_profile = None
        if email:
            try:
                user_profile = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                user_profile = None

        weights = assessment_data.get('weights', {}) or {}

        custom_assessment = _db_call_with_retry(
            lambda: CustomAssessment.objects.create(
                user_profile=user_profile,
                first_name=user_data.get('first_name') or None,
                last_name=user_data.get('last_name') or None,
                email=email,
                organization_name=user_data.get('organization_name') or None,
                role=role,
                sub_roles=assessment_data.get('sub_roles') or [],
                custom_role=assessment_data.get('custom_role') or None,
                experience_level=assessment_data.get('experience_level') or None,
                number_of_questions=number_of_questions,
                time=time_value,
                auto_time=assessment_data.get('auto_time') or None,
                weight_common=int(weights.get('common', 70)),
                weight_role=int(weights.get('role', 15)),
                weight_resume=int(weights.get('resume', 15)),
                extracted_skills=assessment_data.get('extracted_skills') or [],
                suggested_skills=assessment_data.get('suggested_skills') or [],
                common_skills=assessment_data.get('common_skills') or [],
                question_distribution=assessment_data.get('question_distribution') or {},
                removed_skills=assessment_data.get('removed_skills') or [],
                resume_file_name=assessment_data.get('resume_file_name') or None,
            ),
            retries=1,
        )

        return Response(
            {
                'message': 'Custom assessment created successfully.',
                'id': custom_assessment.id,
                'created_at': custom_assessment.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating custom assessment. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_custom_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating custom assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_custom_assessment_view(request, custom_assessment_id: int):
    """
    Fetch a CustomAssessment by ID.
    Used by the frontend to validate a locally-stored draftCustomAssessmentId.
    """
    try:
        try:
            caid = int(custom_assessment_id)
        except (TypeError, ValueError):
            return Response({'error': 'custom_assessment_id must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ca = _db_call_with_retry(lambda: CustomAssessment.objects.get(id=caid), retries=1)
        except CustomAssessment.DoesNotExist:
            return Response({'error': f'CustomAssessment with id {caid} not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                'id': ca.id,
                'created_at': ca.created_at.isoformat() if ca.created_at else None,
                'updated_at': ca.updated_at.isoformat() if getattr(ca, 'updated_at', None) else None,
                'role': ca.role,
                'custom_role': ca.custom_role,
                'experience_level': ca.experience_level,
                'number_of_questions': ca.number_of_questions,
                'time': ca.time,
                'organization_name': ca.organization_name,
                'email': ca.email,
            },
            status=status.HTTP_200_OK
        )

    except OperationalError:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while fetching custom assessment. '
                    'Please check your internet/VPN and DB connectivity, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in get_custom_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while fetching custom assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def create_assessment_view(request):
    """
    Create an Assessment record and associated AssessmentQuestion rows
    from a previously saved CustomAssessment and the final question list.

    Expected request body (JSON):
    {
        "custom_assessment_id": 1,
        "question_ids": [1, 2, 3, ...],  // objective questions in display order
        "coding_question_ids": [10, 11], // optional coding questions (order preserved)
        "coding_allowed_languages": ["python","javascript"] // optional override (fallback to question.languages)
    }
    """
    try:
        # GET: list assessments (simple dashboard feed)
        if request.method == 'GET':
            qs = Assessment.objects.all().order_by('-created_at')

            # Date filtering
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)

            qs = qs[:500]
            results = []
            for a in qs:
                results.append(
                    {
                        'id': a.id,
                        'name': a.name,
                        'display_name': a.display_name,
                        'role': a.role,
                        'experience_level': a.experience_level,
                        'assessment_type': getattr(a, 'assessment_type', None),
                        'total_questions': a.total_questions,
                        'coding_question_count': getattr(a, 'coding_question_count', 0),
                        'total_time': a.total_time,
                        'total_candidates': getattr(a, 'total_candidates', 0),
                        'invited': getattr(a, 'invited', 0),
                        'submitted': getattr(a, 'submitted', 0),
                        'evaluated': getattr(a, 'evaluated', 0),
                        'shortlisted': getattr(a, 'shortlisted', 0),
                        'on_proctoring': getattr(a, 'on_proctoring', False),
                        'invite_token': str(getattr(a, 'invite_token', '')) if getattr(a, 'invite_token', None) else None,
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                    }
                )
            return Response({'count': len(results), 'results': results}, status=status.HTTP_200_OK)

        custom_assessment_id = request.data.get('custom_assessment_id', None)
        question_ids = request.data.get('question_ids', [])
        coding_question_ids = request.data.get('coding_question_ids', [])
        coding_allowed_languages = request.data.get('coding_allowed_languages', None)
        explicit_name = (request.data.get('name') or '').strip() or None
        explicit_display_name = (request.data.get('display_name') or '').strip() or None
        explicit_role = (request.data.get('role') or '').strip() or None
        explicit_experience_level = (request.data.get('experience_level') or '').strip() or None

        custom_assessment = None
        if custom_assessment_id:
            # DB connections to Supabase can be flaky in dev; retry once on OperationalError
            for attempt in range(2):
                try:
                    custom_assessment = CustomAssessment.objects.get(id=custom_assessment_id)
                    break
                except CustomAssessment.DoesNotExist:
                    return Response(
                        {'error': f'CustomAssessment with id {custom_assessment_id} not found.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                except OperationalError as e:
                    close_old_connections()
                    if attempt == 0:
                        continue
                    return Response(
                        {
                            'error': (
                                'Database connection failed while creating assessment. '
                                'Please check your internet/VPN or Supabase DB host, then try again.'
                            )
                        },
                        status=status.HTTP_503_SERVICE_UNAVAILABLE
                    )

        # IMPORTANT: This is the NEW validation that allows empty question_ids for coding-only assessments
        print(f"[NEW CODE CHECK] Received question_ids={question_ids}, coding_question_ids={coding_question_ids}")
        
        if not isinstance(question_ids, list):
            return Response(
                {'error': '[NEW CODE] question_ids must be an array (can be empty when coding_question_ids are provided).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Coding IDs (optional)
        # Supports [id, id, ...] OR [{id:1, difficulty:...}, ...]
        coding_seen = set()
        ordered_coding_ids = []
        coding_overrides = {} # map id -> dict of overrides

        if isinstance(coding_question_ids, list):
            for item in coding_question_ids:
                cqid_int = None
                overrides = {}
                if isinstance(item, (int, str)):
                    try:
                        cqid_int = int(item)
                    except (TypeError, ValueError):
                        continue
                elif isinstance(item, dict):
                    try:
                        cqid_int = int(item.get('id'))
                        if 'difficulty' in item:
                            overrides['difficulty'] = item['difficulty']
                        if 'time_limit_ms' in item:
                            overrides['time_limit_ms'] = int(item['time_limit_ms'])
                    except (TypeError, ValueError):
                        continue
                
                if cqid_int and cqid_int not in coding_seen:
                    coding_seen.add(cqid_int)
                    ordered_coding_ids.append(cqid_int)
                    if overrides:
                        coding_overrides[cqid_int] = overrides
        
        # Debug: log what we received
        print(f"[DEBUG] create_assessment: question_ids={question_ids}, coding_question_ids={coding_question_ids}, ordered_coding_ids={ordered_coding_ids}")

        # Ensure we use unique IDs while preserving order (objective)
        seen = set()
        ordered_unique_ids = []
        for qid in question_ids:
            try:
                qid_int = int(qid)
            except (TypeError, ValueError):
                continue
            if qid_int not in seen:
                seen.add(qid_int)
                ordered_unique_ids.append(qid_int)

        if not ordered_unique_ids and not ordered_coding_ids:
            return Response(
                {'error': 'Provide at least one objective or coding question ID.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Fetch all referenced questions (objective)
        questions_qs = Question.objects.filter(id__in=ordered_unique_ids) if ordered_unique_ids else Question.objects.none()
        if ordered_unique_ids and questions_qs.count() != len(ordered_unique_ids):
            return Response(
                {'error': 'Some question IDs do not exist.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        coding_qs = CodingQuestion.objects.filter(id__in=ordered_coding_ids, is_active=True) if ordered_coding_ids else []
        if ordered_coding_ids and len(coding_qs) != len(ordered_coding_ids):
            return Response(
                {'error': 'Some coding question IDs are invalid or inactive.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        def _seconds_to_hhmmss(seconds: int) -> str:
            seconds = max(0, int(seconds or 0))
            h = seconds // 3600
            m = (seconds % 3600) // 60
            s = seconds % 60
            return f"{h:02d}:{m:02d}:{s:02d}"

        # Compute total time from actual question list (includes manual questions)
        total_time_seconds = 0
        for q in questions_qs:
            try:
                total_time_seconds += int(getattr(q, 'time_limit', None) or 120)
            except Exception:
                total_time_seconds += 120

        coding_total_seconds = 0
        for cq in coding_qs:
            try:
                # Use override time if provided, otherwise use original question time
                override = coding_overrides.get(cq.id, {})
                if 'time_limit_ms' in override:
                    coding_total_seconds += int(override['time_limit_ms']) // 1000
                else:
                    coding_total_seconds += int(getattr(cq, 'time_limit_ms', None) or 0) // 1000
            except Exception:
                pass
        total_time_seconds += coding_total_seconds

        # Debug: Log the total_time received from frontend vs. calculated
        received_total_time = request.data.get('total_time')
        calculated_total_time = _seconds_to_hhmmss(total_time_seconds)
        print(f"[DEBUG] create_assessment: received_total_time={received_total_time}, calculated_total_time={calculated_total_time}, coding_total_seconds={coding_total_seconds}")

        # New fields for split assessment
        # Use request.data and ensure defaults if None is passed
        objective_time_limit = request.data.get('objective_time_limit')
        coding_time_limit = request.data.get('coding_time_limit')
        
        has_objective_cutoff_val = request.data.get('has_objective_cutoff')
        has_objective_cutoff = bool(has_objective_cutoff_val) if has_objective_cutoff_val is not None else False
        
        min_objective_pass_percentage = float(request.data.get('min_objective_pass_percentage') or 0.0)
        weightage_objective = int(request.data.get('weightage_objective') or 0)
        weightage_coding = int(request.data.get('weightage_coding') or 100)

        # Create Assessment
        assessment = Assessment.objects.create(
            user_profile=custom_assessment.user_profile if custom_assessment else None,
            custom_assessment=custom_assessment,
            role=explicit_role or (custom_assessment.role if custom_assessment else None),
            experience_level=explicit_experience_level or (custom_assessment.experience_level if custom_assessment else None),
            total_questions=len(ordered_unique_ids),
            total_time=request.data.get('total_time') or _seconds_to_hhmmss(total_time_seconds),
            coding_total_time=_seconds_to_hhmmss(coding_total_seconds) if coding_total_seconds else None,
            coding_question_count=len(ordered_coding_ids),
            min_pass_percentage=float(request.data.get('min_pass_percentage') or 60.0),
            
            # Save new fields
            objective_time_limit=objective_time_limit,
            coding_time_limit=coding_time_limit,
            has_objective_cutoff=has_objective_cutoff,
            min_objective_pass_percentage=min_objective_pass_percentage,
            weightage_objective=weightage_objective,
            weightage_coding=weightage_coding,

            total_points=int(request.data.get('total_points') or 0),
            status='draft',
        )

        # Populate human-friendly name/display_name if missing
        try:
            base_name = (
                explicit_display_name
                or explicit_name
                or getattr(custom_assessment, 'custom_role', None)
                or getattr(custom_assessment, 'role', None)
                or 'Assessment'
            )
            if explicit_display_name:
                assessment.display_name = explicit_display_name
            if explicit_name:
                assessment.name = explicit_name
            if not getattr(assessment, 'display_name', None):
                assessment.display_name = base_name
            if not getattr(assessment, 'name', None):
                assessment.name = f"{base_name} - {assessment.id}"
            assessment.save(update_fields=['display_name', 'name'])
        except Exception:
            pass

        # Map ID -> Question for quick lookup
        questions_by_id = {q.id: q for q in questions_qs}

        # Create AssessmentQuestion entries in the same order,
        # copying a snapshot of all important question fields
        assessment_questions = []
        for index, qid in enumerate(ordered_unique_ids, start=1):
            q = questions_by_id.get(qid)
            if not q:
                continue
            
            # Debug: Print question data to verify it exists
            print(f"Question {q.id}: type={q.question_type}, difficulty={q.difficulty}, time_limit={q.time_limit}")
            
            # Copy all question details as snapshot (use getattr with defaults for safety)
            assessment_questions.append(
                AssessmentQuestion(
                    assessment=assessment,
                    question=q,
                    skill=getattr(q, 'topic', '') or '',
                    order=index,
                    question_type=getattr(q, 'question_type', '') or '',
                    difficulty=getattr(q, 'difficulty', '') or '',
                    time_limit=getattr(q, 'time_limit', None) or 120,
                    option_a=getattr(q, 'option_a', None) or '',
                    option_b=getattr(q, 'option_b', None) or '',
                    option_c=getattr(q, 'option_c', None) or '',
                    option_d=getattr(q, 'option_d', None) or '',
                    correct_answer=getattr(q, 'correct_answer', None) or '',
                    correct_answers=getattr(q, 'correct_answers', None) or [],
                )
            )

        AssessmentQuestion.objects.bulk_create(assessment_questions)

        # Coding snapshots (ordered after objective block, but preserve provided order)
        if ordered_coding_ids:
            coding_by_id = {cq.id: cq for cq in coding_qs}
            coding_allowed = []
            if isinstance(coding_allowed_languages, list):
                coding_allowed = [str(v).strip().lower() for v in coding_allowed_languages if str(v).strip()]
            coding_snapshots = []
            order_offset = len(assessment_questions) + 1
            for idx, cqid in enumerate(ordered_coding_ids, start=0):
                cq = coding_by_id.get(cqid)
                if not cq:
                    continue
                langs = [str(v).strip().lower() for v in (cq.languages or []) if str(v).strip()]
                # Intersection logic: Only show languages that are BOTH in the assessment global list AND supported by this question.
                # If assessment global list is empty, show all question-supported languages.
                if coding_allowed:
                    allowed = [l for l in langs if l in coding_allowed]
                    if not allowed and langs:
                         # Fallback to the first supported language of the question if intersection is empty
                         # (prevents an empty dropdown being replaced by 'everything')
                         allowed = [langs[0]]
                    elif not allowed and getattr(cq, 'language', None):
                         allowed = [str(cq.language).lower()]
                else:
                    allowed = langs or ([str(cq.language).lower()] if getattr(cq, 'language', None) else [])
                ov = coding_overrides.get(cqid, {})
                # Use override if present, else fallback to question default
                t_limit = ov.get('time_limit_ms') if 'time_limit_ms' in ov else int(getattr(cq, 'time_limit_ms', None) or 0)
                diff = ov.get('difficulty') if 'difficulty' in ov else getattr(cq, 'difficulty', '')

                coding_snapshots.append(
                    AssessmentCodingQuestion(
                        assessment=assessment,
                        coding_question=cq,
                        order=order_offset + idx,
                        title=getattr(cq, 'title', '') or '',
                        description=getattr(cq, 'description', '') or '',
                        languages=langs,
                        allowed_languages=allowed,
                        mode=getattr(cq, 'mode', None) or '',
                        starter_code=getattr(cq, 'starter_code', None) or '',
                        template_code=getattr(cq, 'template_code', None) or '',
                        difficulty=diff,
                        time_limit_ms=t_limit,
                        memory_limit_mb=int(getattr(cq, 'memory_limit_mb', None) or 256),
                    )
                )
            AssessmentCodingQuestion.objects.bulk_create(coding_snapshots)

        return Response(
            {
                'message': 'Assessment created successfully.',
                'assessment_id': assessment.id,
                'total_questions': assessment.total_questions,
                'total_time': assessment.total_time,
                'coding_question_count': assessment.coding_question_count,
                'coding_total_time': assessment.coding_total_time,
                'invite_token': str(getattr(assessment, 'invite_token', '')) if getattr(assessment, 'invite_token', None) else None,
            },
            status=status.HTTP_201_CREATED
        )

    except OperationalError as e:
        close_old_connections()
        return Response(
            {
                'error': (
                    'Database connection failed while creating assessment. '
                    'Please check your internet/VPN or Supabase DB host, then try again.'
                )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except Exception as e:
        import traceback
        print(f"Error in create_assessment_view: {str(e)}")
        print(traceback.format_exc())
        return Response(
            {'error': f'An error occurred while creating assessment: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_assessment_public_view(request, token):
    """
    Public (candidate) fetch by invite_token.
    Returns assessment metadata + question list (without correct answers).
    """
    try:
        try:
            assessment = Assessment.objects.get(invite_token=token)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        aq_qs = (
            AssessmentQuestion.objects.filter(assessment=assessment)
            .select_related('question')
            .order_by('order')
        )
        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        questions = []
        for aq in aq_qs:
            questions.append(
                {
                    'id': aq.id,
                    'order': aq.order,
                    'skill': aq.skill,
                    'question_type': aq.question_type,
                    'difficulty': aq.difficulty,
                    'time_limit': aq.time_limit,
                    'question': aq.question.question if aq.question else None,
                    'option_a': aq.option_a,
                    'option_b': aq.option_b,
                    'option_c': aq.option_c,
                    'option_d': aq.option_d,
                }
            )

        acq_qs = (
            AssessmentCodingQuestion.objects.filter(assessment=assessment)
            .select_related('coding_question')
            .order_by('order')
        )
        coding_questions = []
        for acq in acq_qs:
            cq = acq.coding_question
            coding_questions.append(
                {
                    'id': acq.id,
                    'coding_question_id': cq.id if cq else None,
                    'order': acq.order,
                    'title': acq.title,
                    'description': acq.description,
                    'languages': acq.languages or [],
                    'allowed_languages': acq.allowed_languages or [],
                    'mode': acq.mode,
                    'starter_code': acq.starter_code,
                    'template_code': acq.template_code,
                    'time_limit_ms': acq.time_limit_ms,
                    'memory_limit_mb': acq.memory_limit_mb,
                }
            )

        return Response(
            {
                'assessment': {
                    'id': assessment.id,
                    'name': assessment.name,
                    'display_name': assessment.display_name,
                    'role': assessment.role,
                    'experience_level': assessment.experience_level,
                    'total_questions': assessment.total_questions,
                    'total_time': assessment.total_time,
                    'coding_total_time': assessment.coding_total_time,
                    'coding_question_count': assessment.coding_question_count,
                    'invite_token': str(assessment.invite_token) if assessment.invite_token else None,
                },
                'questions': questions,
                'coding_questions': coding_questions,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_assessment_public_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching assessment: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'PATCH'])
@permission_classes([AllowAny])
def get_assessment_detail_view(request, assessment_id: int):
    """
    Fetch or update a single assessment by numeric ID.
    """
    try:
        try:
            a = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return Response({'error': 'Assessment not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'PATCH':
            data = request.data
            if 'name' in data: a.name = data['name']
            if 'display_name' in data: a.display_name = data['display_name']
            if 'role' in data: a.role = data['role']
            if 'experience_level' in data: a.experience_level = data['experience_level']
            if 'min_pass_percentage' in data: 
                try:
                    a.min_pass_percentage = float(data['min_pass_percentage'])
                except ValueError:
                    pass
            if 'total_time' in data: a.total_time = data['total_time']
            a.save()
            return Response({'ok': True, 'message': 'Assessment updated successfully.'})

        return Response(
            {
                'id': a.id,
                'name': a.name,
                'display_name': a.display_name,
                'role': a.role,
                'experience_level': a.experience_level,
                'total_questions': a.total_questions,
                'total_time': a.total_time,
                'invite_token': str(a.invite_token) if getattr(a, 'invite_token', None) else None,
                'created_at': a.created_at.isoformat() if a.created_at else None,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        import traceback
        print(f"Error in get_assessment_detail_view: {str(e)}")
        print(traceback.format_exc())
        return Response({'error': f'An error occurred while fetching assessment: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _is_valid_pan(pan: str) -> bool:
    if not pan:
        return True
    return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan.strip().upper()))



