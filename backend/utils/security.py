from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hash_pwd(pwd: str):
    return pwd_context.hash(pwd)

def verify_pwd(plain_pwd, hashed_ed):
    return pwd_context.verify(plain_pwd, hashed_ed)