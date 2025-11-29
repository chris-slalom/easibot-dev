from enum import StrEnum, auto


class LogType(StrEnum):
    """Logger type."""

    LOCAL = auto()
    CLOUDWATCH = auto()
