from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class TokenEncryptionError(ValueError):
    """Raised when token encryption is unavailable or decryption fails."""


def _fernet() -> Fernet:
    key = get_settings().social_token_encryption_key
    if not key:
        raise TokenEncryptionError(
            "SOCIAL_TOKEN_ENCRYPTION_KEY is required before connecting social accounts."
        )
    try:
        return Fernet(key.encode("utf-8"))
    except (ValueError, TypeError) as exc:
        raise TokenEncryptionError(
            "SOCIAL_TOKEN_ENCRYPTION_KEY must be a valid Fernet key."
        ) from exc


def encrypt_token(token: str) -> str:
    if not token:
        raise TokenEncryptionError("Cannot encrypt an empty token.")
    return _fernet().encrypt(token.encode("utf-8")).decode("utf-8")


def decrypt_token(encrypted_token: str) -> str:
    try:
        return _fernet().decrypt(encrypted_token.encode("utf-8")).decode("utf-8")
    except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
        raise TokenEncryptionError("Stored social token could not be decrypted.") from exc
