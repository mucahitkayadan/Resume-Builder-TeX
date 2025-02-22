from datetime import datetime, timezone

from pymongo import MongoClient

from config.settings import FEATURE_FLAGS

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["user_information"]
users = db["users"]

# Default preferences
default_llm_preferences = {
    "model_type": "Claude",
    "model_name": "claude-3-5-sonnet-20240620",
    "temperature": 0.1,
}

default_section_preferences = {
    "personal_information": "Hardcode",
    "career_summary": "Process",
    "skills": "Process",
    "work_experience": "Process",
    "education": "Process",
    "projects": "Process",
    "awards": "Hardcode",
    "publications": "Hardcode",
}

default_feature_preferences = {
    "check_clearance": FEATURE_FLAGS["check_clearance"],
    "auto_save": True,
    "dark_mode": False,
}

# New detailed preferences structure
default_detailed_preferences = {
    "project_details": {"max_projects": 5, "bullet_points_per_project": 3},
    "work_experience_details": {"max_jobs": 4, "bullet_points_per_job": 3},
    "skills_details": {
        "max_categories": 5,
        "min_skills_per_category": 7,
        "max_skills_per_category": 15,
    },
    "career_summary_details": {"min_words": 15, "max_words": 25},
    "education_details": {"max_entries": 3, "max_courses": 4},
    "cover_letter_details": {"paragraphs": 5, "target_grade_level": 25},
    "awards_details": {"max_awards": 4},
    "publications_details": {"max_publications": 3},
}


def setup_user(user_id: str):
    """Set up or update user preferences"""
    user = {
        "user_id": user_id,
        "email": "mujakayadan@outlook.com",
        "updated_at": datetime.now(timezone.utc),
        "llm_preferences": default_llm_preferences,
        "section_preferences": default_section_preferences,
        "feature_preferences": default_feature_preferences,
        "preferences": default_detailed_preferences,  # Add the detailed preferences
    }

    # Update or insert user
    users.update_one({"user_id": user_id}, {"$set": user}, upsert=True)
    print(f"User {user_id} preferences updated successfully")


def update_llm_preferences(user_id: str, preferences: dict):
    """Update LLM preferences for a user"""
    users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "llm_preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    print(f"LLM preferences updated for user {user_id}")


def update_section_preferences(user_id: str, preferences: dict):
    """Update section preferences for a user"""
    users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "section_preferences": preferences,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    print(f"Section preferences updated for user {user_id}")


if __name__ == "__main__":
    # Set up default user
    setup_user("mujakayadan")
