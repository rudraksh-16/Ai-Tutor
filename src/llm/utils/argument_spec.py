from typing import Any, Optional


class ArgumentSpec:
    def __init__(
        self,
        type: str,
        description: str,
        required: bool,
        manual_arg: bool = False,
        default: Optional[Any] = None,
    ):
        self.type = type
        self.description = description
        self.manual_arg = manual_arg
        self.required = required
        self.default = default
