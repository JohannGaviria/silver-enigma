"""This module contains the ToggleProductStatusUseCase class."""

from src.modules.products.application.dtos.toggle_product_status_dto import (
    ToggleProductStatusCommandDto,
    ToggleProductStatusResponseDto,
)
from src.modules.products.domain.exceptions.product_exception import (
    ProductHasActiveOrdersException,
    ProductNotFoundException,
)
from src.modules.products.domain.ports.unit_of_work.product_lifecycle_unit_of_work_port import (
    ProductLifecycleUnitOfWorkPort,
)
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


class ToggleProductStatusUseCase:
    """Use case for toggling the status of a product."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        product_lifecycle_unit_of_work: ProductLifecycleUnitOfWorkPort,
    ) -> None:
        """Initializes the ToggleProductStatusUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): the logger factory outbound port.
            product_lifecycle_unit_of_work (ProductLifecycleUnitOfWorkPort): the product lifecycle
                unit of work port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.product_lifecycle_unit_of_work = product_lifecycle_unit_of_work

    async def execute(
        self,
        command: ToggleProductStatusCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> ToggleProductStatusResponseDto:
        """Execute the use case that toggles the status of a product.

        This method toggles the status of an existing product with the provided ID.

        Args:
            command (ToggleProductStatusCommandDto): The command to toggle the status of a product.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            ToggleProductStatusResponseDto: The response from use case.

        Raises:
            InsufficientPermissionsException: If the user does not have sufficient permissions.
            ProductNotFoundException: If the product with the given ID does not exist.
            ProductHasActiveOrdersException: If the product has active orders.
        """
        self._logger.info(
            "Executing toggle product status use case.",
            product_id=command.product_id,
            supplier_id=authenticated_user.user_id,
        )

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning(
                "Unauthorized product status toggle attempt.",
                product_id=command.product_id,
                user_id=authenticated_user.user_id,
            )
            raise InsufficientPermissionsException(
                "Only suppliers can toggle product statuses."
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
                    "Don't have permission to toggle product status."
                )

            # Constants for the blocking order statuses
            BLOCKING_ORDER_STATUSES = {
                OrderStatusEnum.CONFIRMED,
                OrderStatusEnum.PROCESSING,
                OrderStatusEnum.SHIPPED,
            }

            # Validate that a product cannot modify its is_active if it has orders
            # with the status CONFIRMED, PROCESSING, or SHIPPED associated with it.
            has_blocking_orders = (
                await uow.orders_query.exists_by_product_id_and_statuses(
                    command.product_id,
                    BLOCKING_ORDER_STATUSES,
                )
            )
            if has_blocking_orders:
                self._logger.warning(
                    "Cannot toggle product status with active orders.",
                    product_id=command.product_id,
                    supplier_id=authenticated_user.user_id,
                )
                raise ProductHasActiveOrdersException(
                    "Cannot toggle product status with active orders."
                )

            # Update the product and persist the changes
            entity = exists_product.update_is_active(command.is_active)
            product = await uow.products.update(entity)
            await uow.commit()

        self._logger.info(
            "Toggled product status successfully.",
            product_id=product.id,
            supplier_id=product.supplier_id,
        )

        return ToggleProductStatusResponseDto(
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
