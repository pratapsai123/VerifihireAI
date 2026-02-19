import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VerifiHireAI_backend.settings')
django.setup()

from api.models import Company

def verify_db_persistence():
    print("--- Verifying Database Persistence ---")
    
    # 1. Write Data
    company_name = "Test Company Persistence"
    print(f"Attempting to create company: {company_name}")
    company = Company.objects.create(name=company_name, domain="test-persistence.com")
    print(f"Created Company ID: {company.id}")
    
    # 2. Read Data
    print("Attempting to retrieve company from DB...")
    retrieved_company = Company.objects.get(id=company.id)
    print(f"Retrieved: {retrieved_company.name} (Domain: {retrieved_company.domain})")
    
    if retrieved_company.name == company_name:
        print("SUCCESS: Data was written and read back correctly!")
    else:
        print("FAILURE: Data mismatch.")
        
    # 3. Clean up
    print("Cleaning up test data...")
    retrieved_company.delete()
    print("Test data deleted.")
    print("--------------------------------------")

if __name__ == "__main__":
    try:
        verify_db_persistence()
    except Exception as e:
        print(f"ERROR: {e}")
