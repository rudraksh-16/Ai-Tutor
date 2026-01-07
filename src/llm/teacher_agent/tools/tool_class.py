from uuid import UUID


class Tool:
    def __init__(self, func, args_class, description):
        self.func = func
        self.name = func.__name__
        self.description = description
        self.args_class = args_class

    def execute(self, **kwargs):
        return self.func(**kwargs)

    def schema(self):
        properties = {}
        required = []

        for name, args in self.args_class.args:
            prop = {"type": self._map_type(args.type), "description": args.description}
            if args.enum:
                prop["enum"] = args.enum

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
