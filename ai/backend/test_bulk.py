import requests

# Create dummy PDFs
def create_dummy_pdf(filename, content):
    with open(filename, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/MediaBox [0 0 612 792]\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(" + content.encode() + b") Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000224 00000 n\n0000000312 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n406\n%%EOF")

create_dummy_pdf("resume1.pdf", "Python Developer with Django experience")
create_dummy_pdf("resume2.pdf", "Java Developer with Spring experience")

url = "http://localhost:8000/api/candidates/match/"
# Multiple files with same key 'resume'
files = [
    ('resume', ('resume1.pdf', open('resume1.pdf', 'rb'), 'application/pdf')),
    ('resume', ('resume2.pdf', open('resume2.pdf', 'rb'), 'application/pdf'))
]
data = {'job_description': 'Looking for a Python Developer.'}

print(f"Testing bulk upload to: {url}")
try:
    response = requests.post(url, files=files, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Request failed: {e}")
