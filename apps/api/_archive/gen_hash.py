from passlib.context import CryptContext
try:
    pwd_context = CryptContext(schemes=['argon2'], deprecated='auto')
    print(pwd_context.hash('admin'))
except Exception as e:
    print(f"Error: {e}")
