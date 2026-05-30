"""This module contains the CreateProductUseCase class."""

from src.modules.products.application.dtos.create_product_dto import (
    CreateProductCommandDto,
    CreateProductResponseDto,
)
from src.modules.products.domain.entities.product_entity import ProductEntity
from src.modules.products.domain.ports.unit_of_work.product_unit_of_work_port import (
    ProductUnitOfWorkPort,
)
from src.modules.products.domain.value_objects.product_name_vo import ProductNameVO
from src.modules.products.domain.value_objects.unit_price_vo import UnitPriceVO
from src.shared.application.dtos.authenticated_user_dto import (
    AuthenticatedUserCommandDto,
)
from src.shared.domain.enums.user_role_enum import UserRoleEnum
from src.shared.domain.exceptions.session_exception import (
    InsufficientPermissionsException,
)
from src.shared.domain.ports.outbound.logger_factory_outbound_port import (
    LoggerFactoryOutboundPort,
)


class CreateProductUseCase:
    """Use case for creating a new product."""

    def __init__(
        self,
        logger_factory_outbound: LoggerFactoryOutboundPort,
        product_unit_of_work: ProductUnitOfWorkPort,
    ) -> None:
        """Initializes the CreateProductUseCase.

        Args:
            logger_factory_outbound (LoggerFactoryOutboundPort): The logger factory
                outbound port.
            product_unit_of_work (ProductUnitOfWorkPort): The product unit of work port.
        """
        self._logger = logger_factory_outbound.get_logger(__name__)
        self.product_unit_of_work = product_unit_of_work

    async def execute(
        self,
        command: CreateProductCommandDto,
        authenticated_user: AuthenticatedUserCommandDto,
    ) -> CreateProductResponseDto:
        """Execute the use case that creates a product.

        This method creates a new product and persists it to the database using
        the unit of work port.

        Args:
            command (CreateProductCommandDto): The command to execute.
            authenticated_user (AuthenticatedUserCommandDto): The authenticated user.

        Returns:
            CreateProductResponseDto: The response from the use case.
        """
        self._logger.info("Executing create product use case.")

        # Value Objects are validated eagerly at construction time, so domain
        # exceptions will propagate before we open the transaction.
        name = ProductNameVO(command.name)
        unit_price = UnitPriceVO(command.unit_price)

        # Authorization check
        if authenticated_user.role != UserRoleEnum.SUPPLIER:
            self._logger.warning("Unauthorized product creation attempt.")
            raise InsufficientPermissionsException(
                "Only suppliers can create products."
            )

        async with self.product_unit_of_work as uow:
            # Create and persist the new product
            entity = ProductEntity.create(
                supplier_id=authenticated_user.user_id,
                name=name,
                description=command.description,
                unit_of_measure=command.unit_of_measure,
                unit_price=unit_price,
            )
            product = await uow.products.save(entity)
            await uow.commit()

        self._logger.info(
            "Created product successfully.",
            product_id=str(product.id),
            supplier_id=str(product.supplier_id),
        )

        return CreateProductResponseDto(
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
