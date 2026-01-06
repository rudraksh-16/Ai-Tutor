from typing import Any, Optional, Type


class ArgumentSpec:
    def __init__(
        self,
        type: str,
        description: str,
        required: bool,
        default: Optional[Any] = None,
    ):
        self.type = type
        self.description = description
        self.required = required
        self.default = default
