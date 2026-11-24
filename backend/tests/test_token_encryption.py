from types import SimpleNamespace

import pytest
from cryptography.fernet import Fernet

from app.services import token_encryption


def test_token_encryption_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    key = Fernet.generate_key().decode()
    monkeypatch.setattr(
        token_encryption,
        "get_settings",
        lambda: SimpleNamespace(social_token_encryption_key=key),
    )

    encrypted = token_encryption.encrypt_token("sensitive-access-token")

    assert encrypted != "sensitive-access-token"
    assert token_encryption.decrypt_token(encrypted) == "sensitive-access-token"


def test_token_encryption_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        token_encryption,
        "get_settings",
        lambda: SimpleNamespace(social_token_encryption_key=None),
    )

    with pytest.raises(token_encryption.TokenEncryptionError, match="required"):
        token_encryption.encrypt_token("token")


def test_token_encryption_rejects_invalid_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        token_encryption,
        "get_settings",
        lambda: SimpleNamespace(social_token_encryption_key="invalid"),
    )

    with pytest.raises(token_encryption.TokenEncryptionError, match="valid Fernet key"):
        token_encryption.encrypt_token("token")
