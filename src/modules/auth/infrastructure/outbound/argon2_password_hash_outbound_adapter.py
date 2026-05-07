"""This module contains the Argon2PasswordHashOutboundAdapter class."""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.modules.auth.domain.ports.outbound.password_hash_outbound_port import (
    PasswordHashOutboundPort,
)
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO
from src.modules.auth.domain.value_objects.plain_password_vo import PlainPasswordVO


class Argon2PasswordHashOutboundAdapter(PasswordHashOutboundPort):
    """Adapter for hashing passwords using the Argon2 algorithm.

    This adapter implements the PasswordHashOutboundPort interface
    and uses the argon2 library to hash passwords securely.
    """

    def __init__(
        self, time_cost: int = 3, memory_cost: int = 65536, parallelism: int = 4
    ) -> None:
        """Initialize the Argon2 password hasher with specific parameters.

        Args:
            time_cost (int): The number of iterations (default is 3).
            memory_cost (int): The amount of memory to use (default is 65536 KB).
            parallelism (int): The number of parallel threads to use (default is 4).
        """
        self._hasher = PasswordHasher(time_cost, memory_cost, parallelism)

    def hash(self, plain_password: PlainPasswordVO) -> PasswordHashVO:
        """Hash the plain password using Argon2 algorithm.

        Args:
            plain_password (PlainPasswordVO): The plain password to be hashed.

        Returns:
            PasswordHashVO: The hashed password value object.
        """
        hashed = self._hasher.hash(str(plain_password))
        return PasswordHashVO(hashed)

    def verify(
        self, plain_password: PlainPasswordVO, password_hash: PasswordHashVO
    ) -> bool:
        """Verify that the plain password matches the hashed password.

        Args:
            plain_password (PlainPasswordVO): The plain password to verify.
            password_hash (PasswordHashVO): The hashed password to compare against.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        try:
            return self._hasher.verify(str(password_hash), str(plain_password))
        except VerifyMismatchError:
            return False
