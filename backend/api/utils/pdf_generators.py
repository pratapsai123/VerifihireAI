from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io

def generate_assessment_sample_pdf():
    """
    Generates a sample assessment PDF showing MCQ, MSQ, and TF formats.
    Returns: BytesIO object containing the PDF data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles - use clone() to avoid modifying base styles globally
    title_style = styles['Heading1'].clone('title_style', alignment=1)
    
    question_style = styles['BodyText'].clone('question_style', fontName='Helvetica-Bold', textColor=colors.black)
    
    option_style = styles['BodyText'].clone('option_style', leftIndent=20, textColor=colors.black)
    
    correct_option_style = styles['BodyText'].clone('correct_option_style', leftIndent=20, textColor=colors.darkgreen, fontName='Helvetica-Bold')
    
    answer_style = styles['BodyText'].clone('answer_style', textColor=colors.darkgreen, leftIndent=20, fontName='Helvetica-Bold')
    
    section_style = styles['Heading2'].clone('section_style', textColor=colors.black)

    elements = []

    # Title
    elements.append(Paragraph("VerifiHireAI - Assessment PDF Format Guide", title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("This document demonstrates the supported formats for uploading questions. "
                             "You can use these patterns in your own PDF/Word files.", styles['Italic']))
    elements.append(Spacer(1, 20))

    # --- MCQ Section ---
    elements.append(Paragraph("1. Multiple Choice Question (MCQ)", section_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Q1. Which of the following is a core principle of React?", question_style))
    elements.append(Paragraph("A) Two-way data binding", option_style))
    elements.append(Paragraph("B) Component-based architecture", correct_option_style))
    elements.append(Paragraph("C) Direct DOM manipulation", option_style))
    elements.append(Paragraph("D) Global state by default", option_style))
    elements.append(Paragraph("Answer: B", answer_style))
    elements.append(Spacer(1, 20))

    # --- MSQ Section ---
    elements.append(Paragraph("2. Multiple Select Question (MSQ)", section_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Q2. Select all valid React Hooks from the list below:", question_style))
    elements.append(Paragraph("A) useState", correct_option_style))
    elements.append(Paragraph("B) useEffect", correct_option_style))
    elements.append(Paragraph("C) useModel", option_style))
    elements.append(Paragraph("D) useContext", correct_option_style))
    elements.append(Paragraph("Answer: A, B, D", answer_style))
    elements.append(Spacer(1, 20))

    # --- TF Section ---
    elements.append(Paragraph("3. True / False (TF)", section_style))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Q3. JSX is mandatory for building React applications.", question_style))
    elements.append(Paragraph("A) True", option_style))
    elements.append(Paragraph("B) False", correct_option_style))
    elements.append(Paragraph("Answer: False", answer_style))
    elements.append(Spacer(1, 20))

    # --- Tips Section ---
    elements.append(Spacer(1, 30))
    tip_title_style = styles['Heading3'].clone('tip_title_style', textColor=colors.black)
    elements.append(Paragraph("Important Tips:", tip_title_style))
    elements.append(Spacer(1, 10))

    tip_style = styles['BodyText']
    # Use clones to avoid modifying the base styles globally
    tip_bold_style = styles['BodyText'].clone('tip_bold_style', fontName='Helvetica-Bold', textColor=colors.black)
    tip_sub_style = styles['BodyText'].clone('tip_sub_style', leftIndent=20)

    # Tip 1: Question Numbering
    elements.append(Paragraph("• Question Numbering:", tip_bold_style))
    elements.append(Paragraph("Use formats like:", tip_style))
    elements.append(Paragraph("- Q1.", tip_sub_style))
    elements.append(Paragraph("- Q2.", tip_sub_style))
    elements.append(Paragraph("- 1.", tip_sub_style))
    elements.append(Paragraph("- 2.", tip_sub_style))
    elements.append(Spacer(1, 10))

    # Tip 2: Options Format
    elements.append(Paragraph("• Options Format:", tip_bold_style))
    elements.append(Paragraph("Use:", tip_style))
    elements.append(Paragraph("- A), B), C), D)", tip_sub_style))
    elements.append(Paragraph("OR", tip_style))
    elements.append(Paragraph("- A., B., C., D.", tip_sub_style))
    elements.append(Spacer(1, 10))

    # Tip 3: Answer Line
    elements.append(Paragraph("• Answer Line:", tip_bold_style))
    elements.append(Paragraph("Start answers using:", tip_style))
    elements.append(Paragraph("Answer: B", tip_sub_style))
    elements.append(Paragraph("Answer: A, C", tip_sub_style))
    elements.append(Paragraph("Answer: True", tip_sub_style))
    elements.append(Spacer(1, 10))

    # Tip 4: File Types
    elements.append(Paragraph("• Supported File Types:", tip_bold_style))
    elements.append(Paragraph("- PDF (.pdf)", tip_sub_style))
    elements.append(Paragraph("- Microsoft Word (.docx)", tip_sub_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer
