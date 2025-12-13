import logging

from tools.logger import CloudWatchFormatter, LocalFormatter, Logger, LogType
from tools.logger.color import LogColor
from tools.logger.style import LogStyle


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


class TestLocalFormatter:
    """Test class for LocalFormatter."""

    def setup_method(self) -> None:
        """Set up formatter."""
        self.formatter = LocalFormatter()

    def test_formatter_initialization(self) -> None:
        """Test formatter initialization."""
        assert self.formatter is not None
        assert hasattr(self.formatter, "formats")
        assert len(self.formatter.formats) == 5

    def test_format_debug(self) -> None:
        """Test debug level formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="debug message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        assert "debug message" in formatted
        assert "test" in formatted

    def test_format_info(self) -> None:
        """Test info level formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="info message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        assert "info message" in formatted
        assert "test" in formatted

    def test_format_warning(self) -> None:
        """Test warning level formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="warning message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        assert "warning message" in formatted
        assert "test" in formatted

    def test_format_error(self) -> None:
        """Test error level formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="error message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        assert "error message" in formatted
        assert "test" in formatted

    def test_format_critical(self) -> None:
        """Test critical level formatting."""
        record = logging.LogRecord(
            name="test",
            level=logging.CRITICAL,
            pathname="test.py",
            lineno=1,
            msg="critical message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        assert "critical message" in formatted
        assert "test" in formatted


class TestCloudWatchFormatter:
    """Test class for CloudWatchFormatter."""

    def setup_method(self) -> None:
        """Set up formatter."""
        self.formatter = CloudWatchFormatter()

    def test_formatter_initialization(self) -> None:
        """Test formatter initialization."""
        assert self.formatter is not None

    def test_format(self) -> None:
        """Test CloudWatch formatting."""
        import json

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        assert parsed["name"] == "test_logger"
        assert parsed["line"] == 42
        assert parsed["message"] == "test message"

    def test_format_with_function(self) -> None:
        """Test CloudWatch formatting with function name."""
        import json

        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=100,
            msg="error message",
            args=(),
            exc_info=None,
            func="test_function",
        )
        formatted = self.formatter.format(record)
        parsed = json.loads(formatted)
        assert parsed["func"] == "test_function"
        assert parsed["message"] == "error message"


class TestLogType:
    """Test class for LogType enum."""

    def test_log_type_values(self) -> None:
        """Test LogType enum values."""
        assert LogType.LOCAL == "local"
        assert LogType.CLOUDWATCH == "cloudwatch"

    def test_log_type_membership(self) -> None:
        """Test LogType enum membership."""
        assert LogType.LOCAL in LogType
        assert LogType.CLOUDWATCH in LogType


class TestLogColor:
    """Test class for LogColor enum."""

    def test_color_values(self) -> None:
        """Test LogColor enum values exist."""
        assert LogColor.NORMAL is not None
        assert LogColor.BLACK is not None
        assert LogColor.RED is not None
        assert LogColor.GREEN is not None
        assert LogColor.YELLOW is not None
        assert LogColor.BLUE is not None
        assert LogColor.PURPLE is not None
        assert LogColor.CYAN is not None
        assert LogColor.GREY is not None
        assert LogColor.BLOOD is not None

    def test_color_ansi_codes(self) -> None:
        """Test LogColor ANSI codes are strings."""
        for color in LogColor:
            assert isinstance(color.value, str)
            assert color.value.startswith("\033[")


class TestLogStyle:
    """Test class for LogStyle enum."""

    def test_style_values(self) -> None:
        """Test LogStyle enum values exist."""
        assert LogStyle.BOLD is not None
        assert LogStyle.ULINE is not None
        assert LogStyle.BLINK is not None
        assert LogStyle.INVERT is not None
        assert LogStyle.RESET is not None

    def test_style_ansi_codes(self) -> None:
        """Test LogStyle ANSI codes are strings."""
        for style in LogStyle:
            assert isinstance(style.value, str)
            assert "\033[" in style.value or "\x1b[" in style.value
