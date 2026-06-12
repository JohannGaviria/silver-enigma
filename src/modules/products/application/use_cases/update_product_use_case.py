"""This module contains the UpdateProductUseCase class."""

from src.modules.products.application.dtos.update_product_dto import (
    UpdateProductCommandDto,
    UpdatedProductResponseDto,
)
from src.modules.products.domain.exceptions.product_exception import (
    ProductNotFoundException,
)
from src.modules.products.domain.exceptions.product_referenced_order_exception import (
    ProductHasActiveOrdersException,
)
from src.modules.products.domain.ports.unit_of_work.product_lifecycle_unit_of_work_port import (
    ProductLifecycleUnitOfWorkPort,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.order_status_enum import OrderStatusEnum
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class UpdateProductUseCase:
    """Use case for product update.

    This use case updates the name, description, unit of measure, and unit price of a product.
    """

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        product_lifecycle_unit_of_work: ProductLifecycleUnitOfWorkPort,
    ) -> None:
        """Initializes the UpdateProductUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): the logger factory outbound port.
            product_lifecycle_unit_of_work (ProductLifecycleUnitOfWorkPort): the product lifecycle
                unit of work port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.product_lifecycle_unit_of_work = product_lifecycle_unit_of_work

    async def execute(
        self,
        command: UpdateProductCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> UpdatedProductResponseDto:
        """Execute the use case that updates a product.

        This method updates an existing product with is provided
        optional values and persists it in the database.

        Args:
            command (UpdateProductCommandDto): The command to update product with its optional values.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            UpdateProductResponseDto: The response from use case.

        Raises:
            InsufficientPermissionsException: If the user does not have sufficient permissions.
            ProductNotFoundException: If the product with the given ID does not exist.
        """
        self._logger.info(
            "Executing update product use case.",
            product_id=command.product_id,
            supplier_id=authenticated_user.user_id,
        )

        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized product update attempt.",
                user_id=authenticated_user.user_id,
                actor_role=authenticated_user.role,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can update products."
            )

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        # If the value objects are None, they will be set to None in the entity.
        name = ProductNameVO(command.name) if command.name is not None else None
        unit_price = (
            UnitPriceVO(command.unit_price) if command.unit_price is not None else None
        )

        async with self.product_lifecycle_unit_of_work as uow:
            # Find the product by ID and check if it exists
            exists_product = await uow.products.find_by_id(command.product_id)
            if exists_product is None:
                self._logger.warning(
                    "Product not found.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ProductNotFoundException()

            # Check if the product belongs to the authenticated supplier
            if exists_product.supplier_id != authenticated_user.user_id:
                self._logger.warning(
                    "The product does not belong to the authenticated supplier.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise InsufficientPermissionsException(
                    "Don't have permission to update product."
                )

            # Constants for the blocking order statuses
            BLOCKING_ORDER_STATUSES = {
                OrderStatusEnum.CONFIRMED,
                OrderStatusEnum.PROCESSING,
                OrderStatusEnum.SHIPPED,
            }

            # Validate that a product cannot be updated if it has orders
            # in the CONFIRMED, PROCESSING, or SHIPPED status associated with it.
            has_blocking_orders = (
                await uow.orders_query.exists_by_product_id_and_statuses(
                    command.product_id,
                    BLOCKING_ORDER_STATUSES,
                )
            )
            if has_blocking_orders:
                self._logger.warning(
                    "Cannot update product with active orders.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ProductHasActiveOrdersException(
                    "Cannot update product with active orders."
                )

            # Update the product and persist the changes
            entity = exists_product.update(
                name=name,
                description=command.description,
                unit_of_measure=command.unit_of_measure,
                unit_price=unit_price,
            )
            product = await uow.products.update(entity)
            await uow.commit()

        self._logger.info(
            "Updated product successfully.",
            product_id=product.id,
            supplier_id=product.supplier_id,
        )

        return UpdatedProductResponseDto(
            id=product.id,
            supplier_id=product.supplier_id,
            name=str(product.name),
            description=product.description,
            unit_of_measure=product.unit_of_measure,
            unit_price=product.unit_price.value(),
            is_active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
