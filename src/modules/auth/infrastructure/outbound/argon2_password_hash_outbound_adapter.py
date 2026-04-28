"""This module contains the Argon2PasswordHashOutboundAdapter class."""

from argon2 import PasswordHasher

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

    def __init__(self) -> None:
        """Initialize the Argon2 password hasher with specific parameters.

        The parameters used are:
            - time_cost: The number of iterations (default is 3).
            - memory_cost: The amount of memory to use (default is 65536 KB).
            - parallelism: The number of parallel threads to use (default is 4).
        """
        self._hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)

    def hash(self, plain_password: PlainPasswordVO) -> PasswordHashVO:
        """Hash the plain password using Argon2 algorithm.

        Args:
            plain_password (PlainPasswordVO): The plain password to be hashed.

        Returns:
            PasswordHashVO: The hashed password value object.
        """
        hashed = self._hasher.hash(str(plain_password))
        return PasswordHashVO(hashed)
