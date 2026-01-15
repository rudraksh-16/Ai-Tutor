from typing import Any, Optional, Type


class ArgumentSpec:
    def __init__(
        self,
        type: Type,
        description: str,
        required: bool = True,
        default: Optional[Any] = None,
    ):
        self.type = type
        self.description = description
        self.required = required
        self.default = default
