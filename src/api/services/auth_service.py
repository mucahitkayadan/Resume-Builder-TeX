from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from ..schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from src.core.database.factory import get_unit_of_work
from passlib.context import CryptContext
from config.settings import settings
import logging
from src.core.database.models.user import User, UserPreferences

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def create_user(self, user_data: UserCreate):
        try:
            with self.uow:
                # Check if user exists
                existing_user = self.uow.users.get_by_email(user_data.email)
                if existing_user:
                    raise Exception("User with this email already exists")

                # Check if user_id is taken
                existing_user = self.uow.users.get_by_user_id(user_data.user_id)
                if existing_user:
                    raise Exception("This user ID is already taken")

                now = datetime.utcnow()
                default_preferences = UserPreferences().model_dump()
                
                user = User(
                    user_id=user_data.user_id,
                    email=user_data.email,
                    full_name=user_data.full_name,
                    hashed_password=pwd_context.hash(user_data.password),
                    is_active=True,
                    is_superuser=False,
                    last_login=now,
                    created_at=now,
                    updated_at=now,
                    preferences=default_preferences
                )
                created_user = self.uow.users.add(user)
                self.uow.commit()
                
                return UserResponse(
                    user_id=created_user.user_id,
                    email=created_user.email,
                    full_name=created_user.full_name,
                    created_at=created_user.created_at,
                    updated_at=created_user.updated_at,
                    preferences=default_preferences
                )
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise

    async def login_user(self, credentials: UserLogin):
        try:
            with self.uow:
                user = self.uow.users.get_by_email(credentials.email)
                if not user:
                    logger.error(f"User not found with email: {credentials.email}")
                    raise Exception("Invalid credentials")

                if not pwd_context.verify(credentials.password, user.hashed_password):
                    logger.error("Password verification failed")
                    raise Exception("Invalid credentials")

                # Update last login
                user.last_login = datetime.utcnow()
                self.uow.users.update(user)
                self.uow.commit()

                # Generate JWT token
                token_data = {
                    "sub": user.user_id,
                    "email": user.email,
                    "exp": datetime.utcnow() + timedelta(days=1)
                }
                token = jwt.encode(
                    token_data, 
                    settings.jwt_secret_key, 
                    algorithm=settings.jwt_algorithm
                )
                logger.info(f"Login successful for user: {user.user_id}")
                return token
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise

    async def get_user_by_id(self, user_id: str):
        with self.uow:
            return self.uow.users.get_by_user_id(user_id)

    async def update_user(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        try:
            with self.uow:
                user = self.uow.users.get_by_id(user_id)
                if not user:
                    raise Exception("User not found")
                
                # Update fields
                if user_data.full_name:
                    user.full_name = user_data.full_name
                if user_data.email:
                    user.email = user_data.email
                if user_data.preferences:
                    user.preferences.update(user_data.preferences)
                
                user.updated_at = datetime.utcnow()
                self.uow.commit()
                
                return UserResponse.from_orm(user)
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise