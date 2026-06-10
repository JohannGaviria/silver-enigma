from dataclasses import FrozenInstanceError
from decimal import Decimal
from uuid import UUID

import pytest
from faker import Faker

from src.modules.products.domain.enums.unit_of_measure_enum import (
    UnitOfMeasureEnum,
)
from src.modules.products.domain.value_objects.available_stock_vo import (
    AvailableStockVO,
)
from src.modules.products.domain.value_objects.product_stock_item_vo import (
    ProductStockItemVO,
)
from src.modules.products.domain.value_objects.total_stock_vo import (
    TotalStockVO,
)


class TestProductStockItemVO:
    # ---------------------------------------------------------------------------
    # creation
    # ---------------------------------------------------------------------------

    def test_should_create_product_stock_item_vo_when_valid_data_is_provided(
        self,
        faker: Faker,
    ) -> None:
        """Test that a ProductStockItemVO can be created successfully."""
        product_id = UUID(faker.uuid4())
        name = faker.company()
        description = faker.text(max_nb_chars=100)
        unit_price = Decimal(
            str(
                faker.pydecimal(
                    left_digits=4,
                    right_digits=2,
                    positive=True,
                )
            )
        )
        total_stock = TotalStockVO(faker.random_int(min=1, max=1000))
        available_stock = AvailableStockVO(
            faker.random_int(min=0, max=total_stock.value())
        )

        product_stock_item = ProductStockItemVO(
            product_id=product_id,
            name=name,
            description=description,
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=unit_price,
            total_stock=total_stock,
            available_stock=available_stock,
        )

        assert product_stock_item.product_id == product_id
        assert product_stock_item.name == name
        assert product_stock_item.description == description
        assert product_stock_item.unit_of_measure == UnitOfMeasureEnum.KG
        assert product_stock_item.unit_price == unit_price
        assert product_stock_item.total_stock == total_stock
        assert product_stock_item.available_stock == available_stock

    # ---------------------------------------------------------------------------
    # immutability
    # ---------------------------------------------------------------------------

    def test_should_raise_exception_when_attempting_to_modify_product_id(
        self,
        faker: Faker,
    ) -> None:
        """Test that ProductStockItemVO is immutable."""
        product_stock_item = ProductStockItemVO(
            product_id=UUID(faker.uuid4()),
            name=faker.company(),
            description=faker.text(max_nb_chars=100),
            unit_of_measure=UnitOfMeasureEnum.UNIT,
            unit_price=Decimal("10.50"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )

        with pytest.raises(FrozenInstanceError):
            product_stock_item.product_id = UUID(  # type: ignore[misc]
                faker.uuid4()
            )

    # ---------------------------------------------------------------------------
    # equality
    # ---------------------------------------------------------------------------

    def test_should_return_equal_product_stock_item_vos_when_data_is_identical(
        self,
    ) -> None:
        """Test that two ProductStockItemVO instances with identical data are equal."""
        product_id = UUID("11111111-1111-1111-1111-111111111111")

        vo1 = ProductStockItemVO(
            product_id=product_id,
            name="Premium Rice",
            description="High quality rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("15.50"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )

        vo2 = ProductStockItemVO(
            product_id=product_id,
            name="Premium Rice",
            description="High quality rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("15.50"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )

        assert vo1 == vo2

    def test_should_return_different_product_stock_item_vos_when_data_differs(
        self,
    ) -> None:
        """Test that two ProductStockItemVO instances with different data are not equal."""
        vo1 = ProductStockItemVO(
            product_id=UUID("11111111-1111-1111-1111-111111111111"),
            name="Premium Rice",
            description="High quality rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("15.50"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )

        vo2 = ProductStockItemVO(
            product_id=UUID("22222222-2222-2222-2222-222222222222"),
            name="Premium Rice",
            description="High quality rice",
            unit_of_measure=UnitOfMeasureEnum.KG,
            unit_price=Decimal("15.50"),
            total_stock=TotalStockVO(100),
            available_stock=AvailableStockVO(80),
        )

        assert vo1 != vo2
