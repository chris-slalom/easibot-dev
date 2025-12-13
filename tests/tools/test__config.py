import pytest

from tools.config import FastAPIKwArgs, Settings


class TestSettings:
    """Test class for Settings."""

    @pytest.mark.usefixtures("settings")
    def test_local(self, settings: Settings) -> None:
        """Test local settings."""
        assert settings.IS_LOCAL

    @pytest.mark.usefixtures("settings")
    def test_fastapi_kwargs(self, settings: Settings) -> None:
        """Test fastapi_kwargs."""
        assert (
            settings.fastapi_kwargs
            == FastAPIKwArgs(
                debug=False,
                title="FastAPI",
                summary=None,
                description="",
                version="0.1.0",
                openapi_url="/openapi.json",
                docs_url="/docs",
                redoc_url="/redoc",
                openapi_prefix="",
            ).model_dump()
        )

    def test_default_values(self) -> None:
        """Test default settings values."""
        settings = Settings(_env_file=None)
        assert settings.IS_LOCAL is False
        assert settings.debug is False
        assert settings.title == "FastAPI"
        assert settings.summary is None
        assert settings.description == ""
        assert settings.version == "0.1.0"
        assert settings.openapi_url == "/openapi.json"
        assert settings.docs_url == "/docs"
        assert settings.redoc_url == "/redoc"
        assert settings.openapi_prefix == ""
        assert settings.api_prefix_v1 == "/api/v1"
        assert settings.allowed_hosts == ["*"]

    def test_fastapi_kwargs_property(self) -> None:
        """Test fastapi_kwargs property returns dict."""
        settings = Settings(_env_file=None)
        kwargs = settings.fastapi_kwargs
        assert isinstance(kwargs, dict)
        assert "debug" in kwargs
        assert "title" in kwargs
        assert "version" in kwargs

    def test_custom_values(self) -> None:
        """Test settings with custom values."""
        settings = Settings(
            _env_file=None,
            debug=True,
            title="CustomAPI",
            version="1.0.0",
            description="Custom Description",
        )
        assert settings.debug is True
        assert settings.title == "CustomAPI"
        assert settings.version == "1.0.0"
        assert settings.description == "Custom Description"


class TestFastAPIKwArgs:
    """Test class for FastAPIKwArgs."""

    def test_model_creation(self) -> None:
        """Test FastAPIKwArgs model creation."""
        kwargs = FastAPIKwArgs(
            debug=True,
            title="Test API",
            version="1.0.0",
            summary="Test Summary",
            description="Test Description",
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_prefix="/api",
        )
        assert kwargs.debug is True
        assert kwargs.title == "Test API"
        assert kwargs.version == "1.0.0"
        assert kwargs.summary == "Test Summary"
        assert kwargs.description == "Test Description"

    def test_model_dump(self) -> None:
        """Test FastAPIKwArgs model_dump method."""
        kwargs = FastAPIKwArgs(
            debug=False,
            title="API",
            version="0.1.0",
            summary=None,
            description="",
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_prefix="",
        )
        dumped = kwargs.model_dump()
        assert isinstance(dumped, dict)
        assert dumped["debug"] is False
        assert dumped["title"] == "API"
        assert dumped["version"] == "0.1.0"

    def test_none_summary(self) -> None:
        """Test FastAPIKwArgs with None summary."""
        kwargs = FastAPIKwArgs(
            debug=False,
            title="API",
            version="1.0.0",
            summary=None,
            description="Test",
            openapi_url="/openapi.json",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_prefix="",
        )
        assert kwargs.summary is None
