import uuid
from django.utils import timezone

def generate_batch_name(role_name):
    """
    Generates a batch name in the format: JDname_DD-MM-YYYY_HH:mm
    Example: python_14-04-2026_12:20
    """
    now = timezone.localtime(timezone.now())
    # Clean role name: no special characters that might break UI/URLs if used as ID
    # But for DISPLAY name, we can keep it relatively clean
    safe_role = str(role_name or "General").strip().replace(" ", "_")
    date_str = now.strftime("%d-%m-%Y_%H:%M")
    return f"{safe_role}_{date_str}"

def generate_batch_id():
    """
    Generates a unique batch ID for internal indexing.
    We'll keep using UUID for ID to ensure uniqueness, 
    but use the generated_batch_name for the user-friendly identifier.
    Actually, most of our grouping is done by batch_id.
    I'll follow the user's request and use the descriptive name AS the ID if possible, 
    or just use it as batch_name and keep batch_id as a UUID-based string for safety.
    """
    return str(uuid.uuid4())
