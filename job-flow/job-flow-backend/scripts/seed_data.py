"""
Data seeding script for JobFlow
Populates database with common questions and initial data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.database.models import Question, UserProfile


# Common questions that appear frequently in job applications
COMMON_QUESTIONS = [
    # Contact Information
    ("First name", "FIRST_NAME", "contact", "text", ["first name", "given name", "name first"]),
    ("Last name", "LAST_NAME", "contact", "text", ["last name", "family name", "surname", "name last"]),
    ("Email address", "EMAIL", "contact", "text", ["email", "e-mail", "email address", "contact email"]),
    ("Phone number", "PHONE", "contact", "text", ["phone", "phone number", "mobile", "telephone", "contact number"]),
    ("LinkedIn profile", "LINKEDIN_URL", "contact", "text", ["linkedin", "linkedin url", "linkedin profile"]),
    ("GitHub profile", "GITHUB_URL", "contact", "text", ["github", "github url", "github profile"]),
    ("Personal website", "PORTFOLIO_URL", "contact", "text", ["website", "portfolio", "personal website", "portfolio url"]),

    # Location
    ("Street address", "ADDRESS_LINE1", "location", "text", ["address", "street address", "address line 1"]),
    ("City", "CITY", "location", "text", ["city", "town"]),
    ("State", "STATE", "location", "text", ["state", "province", "region"]),
    ("ZIP code", "ZIP_CODE", "location", "text", ["zip", "zip code", "postal code", "postcode"]),
    ("Country", "United States", "location", "text", ["country"]),

    # Work Authorization
    ("Are you authorized to work in the United States?", "Yes", "work_auth", "boolean",
     ["authorized to work", "work authorization", "legally authorized", "right to work"]),
    ("Will you now or in the future require sponsorship for employment visa status?", "No", "work_auth", "boolean",
     ["sponsorship", "visa sponsorship", "require sponsorship", "need sponsorship"]),
    ("Do you have a security clearance?", "No", "work_auth", "boolean",
     ["security clearance", "clearance"]),

    # Experience
    ("Years of professional experience", "10", "experience", "number",
     ["years experience", "years of experience", "professional experience", "total experience"]),
    ("Years of experience in Java", "6", "skills", "number",
     ["java experience", "years of java", "experience with java"]),
    ("Years of experience in Python", "10", "skills", "number",
     ["python experience", "years of python", "experience with python"]),
    ("Years of experience in AWS", "4", "skills", "number",
     ["aws experience", "years of aws", "amazon web services experience"]),
    ("Years of experience in distributed systems", "6", "skills", "number",
     ["distributed systems experience", "experience with distributed systems"]),

    # Compensation & Availability
    ("Desired salary", "SALARY_EXPECTATION", "compensation", "text",
     ["salary", "desired salary", "salary expectation", "expected salary", "compensation"]),
    ("What is your current salary?", "CURRENT_SALARY", "compensation", "text",
     ["current salary", "present salary"]),
    ("Minimum acceptable salary", "MIN_SALARY", "compensation", "text",
     ["minimum salary", "salary minimum"]),
    ("Notice period", "2 weeks", "availability", "text",
     ["notice period", "notice", "availability", "how soon can you start"]),
    ("When can you start?", "AVAILABLE_START_DATE", "availability", "text",
     ["start date", "available to start", "when can you start", "earliest start date"]),

    # Preferences
    ("Are you willing to relocate?", "Yes", "preferences", "boolean",
     ["relocate", "willing to relocate", "open to relocation"]),
    ("Are you open to remote work?", "Yes", "preferences", "boolean",
     ["remote work", "work remotely", "remote position"]),
    ("Preferred work location", "Remote", "preferences", "text",
     ["work location", "preferred location", "location preference"]),

    # Education (common)
    ("Highest level of education", "Bachelor's Degree", "education", "select",
     ["education", "highest education", "education level", "degree"]),
    ("University/College name", "UNIVERSITY_NAME", "education", "text",
     ["university", "college", "school name", "institution"]),
    ("Field of study", "Computer Science", "education", "text",
     ["major", "field of study", "degree field", "area of study"]),
    ("Graduation year", "GRADUATION_YEAR", "education", "text",
     ["graduation", "graduation year", "year graduated"]),

    # Work Experience
    ("Current job title", "CURRENT_TITLE", "experience", "text",
     ["current title", "current position", "job title", "current role"]),
    ("Current company", "CURRENT_COMPANY", "experience", "text",
     ["current company", "current employer", "present employer"]),
    ("How did you hear about this position?", "LinkedIn", "general", "text",
     ["how did you hear", "referral source", "how did you find"]),

    # EEO (Equal Employment Opportunity) - Optional
    ("Gender", "Prefer not to disclose", "eeo", "select",
     ["gender", "sex"]),
    ("Race/Ethnicity", "Prefer not to disclose", "eeo", "select",
     ["race", "ethnicity", "race/ethnicity"]),
    ("Veteran status", "I am not a protected veteran", "eeo", "select",
     ["veteran", "veteran status", "military service"]),
    ("Disability status", "I do not have a disability", "eeo", "select",
     ["disability", "disability status", "disabled"]),

    # Cover Letter & Resume
    ("Upload your resume", "RESUME_FILE", "documents", "file",
     ["resume", "cv", "upload resume", "attach resume"]),
    ("Upload your cover letter", "COVER_LETTER_FILE", "documents", "file",
     ["cover letter", "upload cover letter", "attach cover letter"]),

    # Additional Common Questions
    ("Why do you want to work for us?", "I am excited about the opportunity to work with your team and contribute my expertise in distributed systems and backend development.", "motivation", "textarea",
     ["why do you want", "why are you interested", "why this company"]),
    ("What interests you about this role?", "This role aligns perfectly with my background in senior backend engineering and my passion for building scalable systems.", "motivation", "textarea",
     ["what interests you", "why this role", "why this position"]),
    ("Are you comfortable with on-call rotation?", "Yes", "preferences", "boolean",
     ["on-call", "on call", "pager duty"]),
    ("Do you have experience with code review?", "Yes", "skills", "boolean",
     ["code review", "peer review", "reviewing code"]),
    ("Are you comfortable working in an agile environment?", "Yes", "preferences", "boolean",
     ["agile", "scrum", "agile environment"]),
]


def seed_questions(db):
    """Seed common questions into database"""
    print("Seeding common questions...")

    # Check if we need a user profile first
    profile = db.query(UserProfile).first()
    if not profile:
        print("No user profile found. Creating placeholder profile...")
        profile = UserProfile(
            first_name="User",
            last_name="Profile",
            email="user@example.com",
            phone="555-0100",
            work_authorized=True,
            requires_sponsorship=False,
            total_years_experience=10,
            current_title="Senior Software Engineer",
            notice_period_weeks=2
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        print("✓ Placeholder profile created")

    # Seed questions
    added_count = 0
    skipped_count = 0

    for question_text, answer, category, field_type, variants in COMMON_QUESTIONS:
        # Check if question already exists
        existing = db.query(Question).filter(
            Question.question_text == question_text
        ).first()

        if existing:
            skipped_count += 1
            continue

        # Create question
        question = Question(
            user_id=profile.id,
            question_text=question_text,
            answer=answer,
            category=category,
            field_type=field_type,
            keywords=variants,
            variants=variants,
            auto_learned=False,
            user_verified=True,
            times_used=0
        )

        db.add(question)
        added_count += 1

    db.commit()
    print(f"✓ Added {added_count} questions")
    if skipped_count > 0:
        print(f"  Skipped {skipped_count} existing questions")


def main():
    """Main seeding function"""
    print("=" * 60)
    print("JobFlow Data Seeding Script")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("✓ Database initialized")

    # Create session
    db = SessionLocal()

    try:
        # Seed questions
        print("\n2. Seeding common questions...")
        seed_questions(db)

        print("\n" + "=" * 60)
        print("✓ Seeding completed successfully!")
        print("=" * 60)

        # Print statistics
        total_questions = db.query(Question).count()
        total_profiles = db.query(UserProfile).count()

        print(f"\nDatabase Statistics:")
        print(f"  - User Profiles: {total_profiles}")
        print(f"  - Questions: {total_questions}")

        print("\nNext steps:")
        print("  1. Start the backend server: uvicorn app.main:app --reload")
        print("  2. Visit http://localhost:8000/docs to explore the API")
        print("  3. Create/update your user profile via API")
        print("  4. Upload your resume(s)")
        print("  5. Start applying to jobs!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
