from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging
from bson import ObjectId
import hashlib

from models.user import UserCreate, UserInDB, UserResponse, Token, TokenData
from database.mongodb import get_database
from config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self):
        from database.mongodb import get_database
        self.db = get_database()
        self.users_collection = self.db.users
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        # Pre-hash password with SHA256 to avoid bcrypt's 72-byte limit
        password_bytes = hashlib.sha256(plain_password.encode()).hexdigest()
        return pwd_context.verify(password_bytes, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        # Pre-hash password with SHA256 to avoid bcrypt's 72-byte limit
        password_bytes = hashlib.sha256(password.encode()).hexdigest()
        print(f"DEBUG: Hashing password, SHA256 hash: {password_bytes[:20]}...")
        hashed = pwd_context.hash(password_bytes)
        print(f"DEBUG: Bcrypt hash created successfully")
        return hashed
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def verify_token(self, token: str) -> Optional[str]:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return user_id
        except JWTError as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def register_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.users_collection.find_one({"email": user_data.email})
            if existing_user:
                logger.warning(f"User already exists: {user_data.email}")
                return None
            
            # Create user document
            user_dict = {
                "name": user_data.name,
                "email": user_data.email,
                "password_hash": self.get_password_hash(user_data.password),
                "created_at": datetime.utcnow()
            }
            
            result = await self.users_collection.insert_one(user_dict)
            user_dict["_id"] = str(result.inserted_id)
            
            logger.info(f"User registered successfully: {user_data.email}")
            return UserResponse(**user_dict)
            
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return None
    
    async def login_user(self, email: str, password: str) -> Optional[Token]:
        """Login user and return token"""
        try:
            # Find user
            user = await self.users_collection.find_one({"email": email})
            if not user:
                logger.warning(f"User not found: {email}")
                return None
            
            # Verify password
            if not self.verify_password(password, user["password_hash"]):
                logger.warning(f"Invalid password for user: {email}")
                return None
            
            # Create access token
            access_token = self.create_access_token(
                data={"sub": str(user["_id"])}
            )
            
            logger.info(f"User logged in successfully: {email}")
            return Token(access_token=access_token, token_type="bearer")
            
        except Exception as e:
            logger.error(f"Error logging in user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None
            
            user["_id"] = str(user["_id"])
            return UserResponse(**user)
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
