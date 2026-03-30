import psycopg2
import os

def check_raw(pk):
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('DB_NAME', 'user'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD', '1234'),
            host=os.environ.get('DB_HOST', '127.0.0.1'),
            port=os.environ.get('DB_PORT', '5432')
        )
        cur = conn.cursor()
        
        print(f"--- Checking ID {pk} ---")
        
        # Candidate
        try:
            cur.execute("SELECT id, full_name, email, is_deleted FROM ai_candidates_candidate WHERE id = %s", [pk])
            print(f"Candidate table: {cur.fetchone()}")
        except Exception as e:
            print(f"Error checking candidate table: {e}")
            conn.rollback()

        # AIAssessmentSubmission
        try:
            cur.execute("SELECT id, candidate_name, candidate_email, is_deleted FROM ai_assessment_submission WHERE id = %s", [pk])
            print(f"AIAssessmentSubmission table: {cur.fetchone()}")
        except Exception as e:
            print(f"Error checking submission table: {e}")
            conn.rollback()

        # Assessment
        try:
            cur.execute("SELECT id, required_skills, share_token FROM ai_assessments_assessment WHERE id = %s", [pk])
            print(f"Assessment table: {cur.fetchone()}")
        except Exception as e:
            print(f"Error checking assessment table: {e}")
            conn.rollback()

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    check_raw(308)
