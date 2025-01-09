from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from src.core.database.factory import get_unit_of_work
from passlib.context import CryptContext
from config.settings import settings
import logging
from src.core.database.models.user import User, UserPreferences
import os
from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self):
        self.uow = get_unit_of_work()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    async def authenticate_user(self, uow: MongoUnitOfWork, email: str, password: str) -> Optional[User]:
        try:
            user = await uow.users.get_by_email(email)
            if not user:
                return None
            if not self.verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def get_current_user(self, uow: MongoUnitOfWork, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            user = await uow.users.get_by_id(user_id)
            return user
        except JWTError as e:
            logger.error(f"JWT error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None

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