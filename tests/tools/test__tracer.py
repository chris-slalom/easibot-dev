import time

from tools.tracer import Timer


class TestTimer:
    """Test class for Timer."""

    def test_contextmanager(self) -> None:
        """Test for ContextManager."""
        with Timer("ContextManager"):
            pass

    @Timer("Decorator")
    def test_decorator(self) -> None:
        """Test for Decorator."""

    def test_timer_with_sleep(self) -> None:
        """Test timer measures time correctly."""
        timer = Timer("test_sleep")
        with timer:
            time.sleep(0.01)
        assert timer._duration >= 0.01

    def test_timer_properties(self) -> None:
        """Test timer has correct properties."""
        timer = Timer("test_properties")
        assert timer.name == "test_properties"
        with timer:
            pass
        assert hasattr(timer, "start")
        assert hasattr(timer, "end")
        assert timer._duration >= 0

    def test_timer_as_decorator_with_args(self) -> None:
        """Test timer as decorator with function arguments."""

        @Timer("function_with_args")
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)
        assert result == 5

    def test_timer_multiple_uses(self) -> None:
        """Test timer can be used multiple times."""
        timer = Timer("reusable")
        with timer:
            time.sleep(0.001)
        duration1 = timer._duration

        timer2 = Timer("reusable")
        with timer2:
            time.sleep(0.002)
        duration2 = timer2._duration

        assert duration2 > duration1

    def test_timer_name_attribute(self) -> None:
        """Test timer name attribute."""
        timer = Timer("custom_name")
        assert timer.name == "custom_name"
