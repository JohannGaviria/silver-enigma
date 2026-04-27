from dataclasses import FrozenInstanceError

import pytest

from src.modules.auth.domain.exceptions.auth_exception import (
    InvalidPasswordHashException,
)
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO


class TestPasswordHashVO:
    def test_should_return_password_hash_as_string_when_valid_hash_is_provided(
        self, password_hash: str
    ) -> None:
        """Test that the PasswordHashVO returns the password hash as a string when a valid hash is provided."""
        password_hash_vo = PasswordHashVO(password_hash)

        assert str(password_hash_vo) == password_hash

    def test_should_raise_exception_when_password_hash_is_empty(self) -> None:
        """Test that the PasswordHashVO raises an InvalidPasswordHashException when an empty password hash is provided."""
        with pytest.raises(InvalidPasswordHashException):
            PasswordHashVO("")

    def test_should_raise_exception_when_attempting_to_modify_password_hash(
        self, password_hash: str
    ) -> None:
        """Test that the PasswordHashVO raises a FrozenInstanceError when attempting to modify the password hash after creation."""
        password_hash_vo = PasswordHashVO(password_hash)

        with pytest.raises(FrozenInstanceError):
            password_hash_vo.password_hash = password_hash  # type: ignore[misc]
