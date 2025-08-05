from fastapi import Depends
from fastapi_users.manager import BaseUserManager
from app.api.models import User
from app.api.deps import get_user_db

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = "SECRET"      # Use your secret!
    verification_token_secret = "SECRET"        # Use your secret!

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)