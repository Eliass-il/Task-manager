from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
dummy_hash = password_hash.hash("dummypassword")

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, stored_hash: str) -> bool:
    return password_hash.verify(password, stored_hash)