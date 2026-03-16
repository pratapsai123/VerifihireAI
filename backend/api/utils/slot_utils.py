from datetime import datetime, time, timedelta
from django.utils import timezone
from api.models import InterviewSlot, UserProfile

def generate_slots_for_interviewer(interviewer_profile, start_date, days_count=5):
    """
    Generates available slots for an interviewer for the next X days.
    Skips tea breaks and lunch breaks.
    Standard window: 09:00 AM - 05:30 PM (17:30)
    Duration: 45 minutes
    """
    slots_created = 0
    
    # Define breaks
    tea_break_1 = (time(11, 15), time(11, 25))
    lunch_break = (time(13, 0), time(13, 45))
    tea_break_2 = (time(15, 15), time(15, 25))
    
    day_start = time(9, 0)
    day_end = time(17, 30)
    slot_duration = timedelta(minutes=45)
    
    for i in range(days_count):
        current_date = start_date + timedelta(days=i)
        
        # Skip weekends (Optional, User said "holidays no need to take for these approach")
        # if current_date.weekday() >= 5:
        #     continue
            
        current_time = datetime.combine(current_date, day_start)
        end_of_day = datetime.combine(current_date, day_end)
        
        while current_time + slot_duration <= end_of_day:
            slot_start = current_time.time()
            slot_end = (current_time + slot_duration).time()
            
            # Check for overlaps with breaks
            is_break = False
            
            # Helper to check if a range [s1, e1] overlaps with [s2, e2]
            def overlaps(s1, e1, s2, e2):
                return s1 < e2 and s2 < e1
            
            if overlaps(slot_start, slot_end, tea_break_1[0], tea_break_1[1]):
                is_break = True
                # Move time to after break
                current_time = datetime.combine(current_date, tea_break_1[1])
            elif overlaps(slot_start, slot_end, lunch_break[0], lunch_break[1]):
                is_break = True
                current_time = datetime.combine(current_date, lunch_break[1])
            elif overlaps(slot_start, slot_end, tea_break_2[0], tea_break_2[1]):
                is_break = True
                current_time = datetime.combine(current_date, tea_break_2[1])
            
            if not is_break:
                # Double check if slot still fits
                if (current_time + slot_duration).time() <= day_end:
                    # Create slot if it doesn't exist
                    InterviewSlot.objects.get_or_create(
                        interviewer=interviewer_profile,
                        slot_date=current_date,
                        start_time=current_time.time(),
                        end_time=(current_time + slot_duration).time(),
                        defaults={'status': InterviewSlot.STATUS_AVAILABLE}
                    )
                    slots_created += 1
                    current_time += slot_duration
                else:
                    break
            else:
                # If it was a break, current_time was already moved to break end
                continue
                
    return slots_created
