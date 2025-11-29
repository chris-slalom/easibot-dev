from tools.logger import Logger, LogType


class TestLocalLogger:
    """Test class for local logger."""

    def setup_method(self) -> None:
        """Set up logger."""
        self.logger = Logger(name=__name__, log_type=LogType.LOCAL)

    def test_log(self) -> None:
        """Test log method of logger."""
        assert self.logger.debug("debug") is None
        assert self.logger.info("info") is None
        assert self.logger.warning("warning") is None
        assert self.logger.error("error") is None
        assert self.logger.critical("critical") is None

    def test_name(self) -> None:
        """Test correct name of logger."""
        assert self.logger.name == __name__


class TestCloudWatchLogger:
    """Test class for AWS CloudWatch logger."""

    def setup_method(self) -> None:
        """Set up logger."""
        self.logger = Logger(
            name=__name__,
            log_type=LogType.CLOUDWATCH,
        )

    def test_log(self) -> None:
        """Test log method of logger."""
        assert self.logger.debug("debug") is None
        assert self.logger.info("info") is None
        assert self.logger.warning("warning") is None
        assert self.logger.error("error") is None
        assert self.logger.critical("critical") is None

    def test_name(self) -> None:
        """Test correct name of logger."""
        assert self.logger.name == __name__
