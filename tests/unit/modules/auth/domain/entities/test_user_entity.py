from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.auth.domain.entities.user_entity import UserEntity
from src.modules.auth.domain.enums.user_role_enum import UserRoleEnum
from src.modules.auth.domain.value_objects.email_vo import EmailVO
from src.modules.auth.domain.value_objects.name_vo import NameVO
from src.modules.auth.domain.value_objects.password_hash_vo import PasswordHashVO


class TestUserEntity:
    def test_should_create_user_entity_when_valid_data_is_provided(
        self, faker: Faker, password_hash: str
    ) -> None:
        """Test that the UserEntity can be created successfully when valid data is provided."""
        name = NameVO(faker.name())
        email = EmailVO(faker.email())
        password = PasswordHashVO(password_hash)
        role = UserRoleEnum.ADMIN

        user = UserEntity.create(name=name, email=email, password=password, role=role)

        assert user.id is not None
        assert user.name == name
        assert user.email == email
        assert user.password == password
        assert user.role == role
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_should_return_correct_types_for_user_entity_attributes(
        self, faker: Faker, password_hash: str
    ) -> None:
        """Test that the UserEntity attributes return the correct types."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        assert isinstance(user.name, NameVO)
        assert isinstance(user.email, EmailVO)
        assert isinstance(user.password, PasswordHashVO)
        assert isinstance(user.role, UserRoleEnum)

    def test_should_raise_exception_when_attempting_to_modify_user_entity_email(
        self, faker: Faker, password_hash: str
    ) -> None:
        """Test that the UserEntity raises a FrozenInstanceError when attempting to modify the email after creation."""
        user = UserEntity.create(
            name=NameVO(faker.name()),
            email=EmailVO(faker.email()),
            password=PasswordHashVO(password_hash),
            role=UserRoleEnum.ADMIN,
        )

        with pytest.raises(FrozenInstanceError):
            user.email = EmailVO(faker.email())  # type: ignore[misc]

    def test_should_return_equal_user_entities_when_data_is_identical(
        self, faker: Faker, password_hash: str
    ) -> None:
        """Test that two UserEntity instances with identical data are considered equal."""
        name = NameVO(faker.name())
        email = EmailVO(faker.email())
        password = PasswordHashVO(password_hash)

        user1 = UserEntity.create(name, email, password, UserRoleEnum.ADMIN)
        user2 = UserEntity(
            id=user1.id,
            name=name,
            email=email,
            password=password,
            role=UserRoleEnum.ADMIN,
            created_at=user1.created_at,
            updated_at=user1.updated_at,
        )

        assert user1 == user2
