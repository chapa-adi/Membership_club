import bcrypt

# ------------- PASSWORD HASHING -------------

def hash_password(password: str) -> str:
    # Convert to bytes
    password_bytes = password.encode("utf-8")
    # Generate salt and hash   (each time a new salt is produced so no issue evenif same password)
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # Store as string
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    plain_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(plain_bytes, hashed_bytes)
