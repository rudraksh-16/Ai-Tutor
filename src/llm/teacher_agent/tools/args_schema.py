class Args:
    def __init__(self, type=str, description=None, enum=None, required=True):
        self.type = type
        self.description = description
        self.enum = enum
        self.required = required
