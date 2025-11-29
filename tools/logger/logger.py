import logging
import sys

from tools.logger.type import LogType


class Logger(logging.Logger):
    """Logger.

    Examples:
        >>> from tools.logger import Logger
        >>>
        >>>
        >>> logger = Logger(__name__)
        >>> logger.info("Logger")

    """

    def __init__(
        self,
        name: str,
        log_type: LogType = LogType.LOCAL,
    ) -> None:
        """Initialize logger formatter.

        Args:
            name (str): Logger name
            log_type (LogType, optional): Local or CloudWatch.
                                          Defaults to LogType.LOCAL.

        """
        super().__init__(name=name)

        if log_type == LogType.CLOUDWATCH:
            from tools.logger import CloudWatchFormatter

            formatter = CloudWatchFormatter()
            handler = logging.StreamHandler(stream=sys.stdout)

            handler.setFormatter(formatter)
            self.addHandler(handler)
            return

        from tools.logger import LocalFormatter

        formatter = LocalFormatter()
        handler = logging.StreamHandler(stream=sys.stdout)

        handler.setFormatter(formatter)
        self.addHandler(handler)
