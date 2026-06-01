"""This module contains the UnitOfMeasureEnum class."""

from enum import StrEnum


class UnitOfMeasureEnum(StrEnum):
    """Enumeration representing the unit of measure used to quantify products.

    This enumeration defines the supported units used to represent product
    quantities in the system, including measurement units, counting units,
    and packaging units:

    Attributes:
        UNIT (str): Represents an individual product unit.
        KG (str): Represents products measured in kilograms.
        LT (str): Represents products measured in liters.
        BOX (str): Represents products grouped and managed by box.
    """

    UNIT = "UNIT"
    KG = "KG"
    LT = "LT"
    BOX = "BOX"
