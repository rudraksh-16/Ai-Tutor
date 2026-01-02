from enum import Enum

class Status(str, Enum):
    pending = "pending"
    in_process = "in_process"
    completed = "completed"
