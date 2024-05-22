"""Interface representing an annotation."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(eq=True, unsafe_hash=True)
class Annotation:
    """Represents an annotation."""

    slot: str = field(hash=True)
    value: Optional[str] = field(default=None, hash=True)
