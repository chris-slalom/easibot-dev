import logging


class CloudWatchFormatter(logging.Formatter):
    """Formatter for AWS CloudWatch logger."""

    def format(self, record: logging.LogRecord) -> str:
        """Style for AWS CloudWatch logger.

        Args:
            record (logging.LogRecord): Raw log

        Returns:
            str: Log format for AWS CloudWatch

        """
        from pydantic import BaseModel, PositiveInt

        class Record(BaseModel):
            """Record for AWS CloudWatch."""

            name: str
            line: PositiveInt
            func: str
            message: str

        return Record(
            name=record.name,
            line=record.lineno,
            func=record.funcName,
            message=record.getMessage(),
        ).model_dump_json()
