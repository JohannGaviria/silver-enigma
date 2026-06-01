from dataclasses import FrozenInstanceError

import pytest
from faker import Faker

from src.modules.products.domain.exceptions.product_exception import (
    InvalidProductNameException,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO


class TestProductNameVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_product_name_vo_when_name_is_valid(
        self,
        faker: Faker,
    ) -> None:
        """Test that a ProductNameVO can be created when a valid name is provided."""
        name = faker.pystr(min_chars=3, max_chars=149)

        product_name = ProductNameVO(name)

        assert product_name.name == name

    # ---------------------------------------------------------------------------
    # validation
    # ---------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "name",
        [
            "",
            " ",
            "   ",
        ],
    )
    def test_should_raise_exception_when_name_is_empty(
        self,
        name: str,
    ) -> None:
        """Test that an exception is raised when the product name is empty."""
        with pytest.raises(InvalidProductNameException) as exc_info:
            ProductNameVO(name)

        assert "Name cannot be empty." in exc_info.value.errors

    @pytest.mark.parametrize(
        "name",
        [
            "a",
            "ab",
        ],
    )
    def test_should_raise_exception_when_name_is_shorter_than_three_characters(
        self,
        name: str,
    ) -> None:
        """Test that an exception is raised when the product name has fewer than three characters."""
        with pytest.raises(InvalidProductNameException) as exc_info:
            ProductNameVO(name)

        assert "Name must be at least 3 characters long." in exc_info.value.errors

    def test_should_raise_exception_when_name_has_one_hundred_fifty_or_more_characters(
        self,
    ) -> None:
        """Test that an exception is raised when the product name has one hundred fifty or more characters."""
        with pytest.raises(InvalidProductNameException) as exc_info:
            ProductNameVO("a" * 150)

        assert "Name cannot be longer than 150 characters." in exc_info.value.errors

    def test_should_raise_exception_with_multiple_errors_when_name_violates_multiple_rules(
        self,
    ) -> None:
        """Test that all validation errors are returned when the product name violates multiple rules."""
        with pytest.raises(InvalidProductNameException) as exc_info:
            ProductNameVO("")

        assert "Name cannot be empty." in exc_info.value.errors
        assert "Name must be at least 3 characters long." in exc_info.value.errors

    # ---------------------------------------------------------------------------
    # string representation
    # ---------------------------------------------------------------------------

    def test_should_return_name_when_converted_to_string(
        self,
        faker: Faker,
    ) -> None:
        """Test that the string representation returns the product name."""
        name = faker.pystr(min_chars=3, max_chars=149)

        product_name = ProductNameVO(name)

        assert str(product_name) == name

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_name(
        self,
        faker: Faker,
    ) -> None:
        """Test that the ProductNameVO is immutable."""
        product_name = ProductNameVO(
            faker.pystr(min_chars=3, max_chars=149),
        )

        with pytest.raises(FrozenInstanceError):
            product_name.name = faker.word()  # type: ignore[misc]

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_product_name_vos_when_names_are_identical(
        self,
    ) -> None:
        """Test that two ProductNameVO instances with the same value are equal."""
        product_name_1 = ProductNameVO("Rice Premium")
        product_name_2 = ProductNameVO("Rice Premium")

        assert product_name_1 == product_name_2
