class Tool:
    def __init__(self, func, args_schema=None, description: str = None):
        self.func = func
        self.name = func.__name__
        self.description = description
        self.args_schema = args_schema
        self.manual_arg = []

    def execute(self, **kwargs):
        return self.func(**kwargs)

    def schema(self):

        if self.args_schema is None:
            return {
                "type": "function",
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            }
        properties = {}
        required = []
        self.manual_arg = []
        for name, args in self.args_schema.args:
            if args.manual_arg == True:
                self.manual_arg.append(name)
            else:
                prop = {
                    "type": self._map_type(args.type),
                    "description": args.description,
                }
                properties[name] = prop
                if args.required == True:
                    required.append(name)

        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    @staticmethod
    def _map_type(py_type):
        return {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
        }.get(py_type, "string")
