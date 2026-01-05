from typing import Any, Optional, Type


class ArgumentSpec:
    def __init__(
        self,
        type: Type,
        description: str,
        required: bool,
        default: Optional[Any] = None,
    ):
        self.type: str = type
        self.description: str = description
        self.required: bool = required
        self.default: Optional[Any] = default
