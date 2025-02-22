from passlib.context import CryptContext
from pymongo import MongoClient

from config.settings import settings

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Connect to MongoDB
client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_database]


def reset_password(email: str, new_password: str):
    # Hash the new password
    hashed_password = pwd_context.hash(new_password)

    # Update in database
    result = db.users.update_one(
        {"email": email}, {"$set": {"hashed_password": hashed_password}}
    )

    if result.modified_count:
        print(f"Password updated successfully for {email}")
    else:
        print(f"User with email {email} not found")


if __name__ == "__main__":
    email = input("Enter email: ")
    new_password = input("Enter new password: ")
    reset_password(email, new_password)
