"""Settings and configuration for EASI Bot."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # AWS Configuration
    aws_region: str = "us-west-2"
    aws_profile: str | None = None

    # Bedrock Configuration
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    bedrock_region: str = "us-west-2"

    # S3 Configuration
    rag_bucket_name: str = "easibot-rag"

    # Application Configuration
    log_level: str = "INFO"
    environment: str = "development"
    max_iterations: int = 10


# Global settings instance
settings = Settings()
