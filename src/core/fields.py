from pydantic import Field

ENTITIES_REGEX = r"[A-Z]+_[A-Z0-9]+"

some_quantity: float = Field(..., example=2614.6800000000003)
units: str = Field(..., example="TONELADAS")
shift: int = Field(..., example=1)
