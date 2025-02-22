from datetime import datetime

from bson import ObjectId


async def migrate_resumes(db):
    """Migrate existing resumes to new structure"""
    cursor = db.resumes.find({})

    # Use to_list to get all documents from the cursor
    old_resumes = await cursor.to_list(length=None)

    for old_resume in old_resumes:
        new_resume = {
            "user_id": "test_user",
            "version": 1,
            "title": "My Resume",
            "template_id": "default",
            # Content fields
            "personal_information": old_resume.get("personal_information", {}),
            "career_summary": old_resume.get("career_summary", ""),
            "skills": old_resume.get("skills", {}),
            "work_experience": old_resume.get("work_experience", []),
            "education": old_resume.get("education", []),
            "projects": old_resume.get("projects", []),
            "awards": old_resume.get("awards", []),
            "publications": old_resume.get("publications", []),
            # Resume content
            "resume_latex": old_resume.get("latex_content"),
            "resume_pdf": old_resume.get("resume_pdf"),
            # Cover letter content
            "cover_letter_content": old_resume.get("cover_letter_content"),
            "cover_letter_pdf": old_resume.get("cover_letter_pdf"),
            # Timestamps
            "created_at": old_resume.get("created_at", datetime.utcnow()),
            "updated_at": old_resume.get("updated_at", datetime.utcnow()),
        }

        # Insert into new collection
        result = await db.resumes_new.insert_one(new_resume)
        print(f"Migrated resume {result.inserted_id}")


if __name__ == "__main__":
    import asyncio

    from motor.motor_asyncio import AsyncIOMotorClient

    async def main():
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client.user_information  # Your database name

        try:
            # Create backup by copying the collection
            if "resumes_backup" in await db.list_collection_names():
                print("Dropping existing backup collection")
                await db.resumes_backup.drop()

            print("Creating backup of resumes collection")
            await db.resumes.aggregate([{"$out": "resumes_backup"}]).to_list(None)
            print("Backup created successfully")

            # Create new collection if it doesn't exist
            if "resumes_new" in await db.list_collection_names():
                print("Dropping existing resumes_new collection")
                await db.resumes_new.drop()

            # Run migration
            print("Starting migration...")
            await migrate_resumes(db)
            print("Migration completed successfully")

        except Exception as e:
            print(f"Error during migration: {str(e)}")
            import traceback

            traceback.print_exc()
        finally:
            client.close()

    # Run the migration
    asyncio.run(main())
