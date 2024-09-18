from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Main setup for the trip backend server."""

    # APP SETTINGS
    ENVIRONMENT: str = Field(description="Environment type", default="local")
    PORT: int = Field(description="Server port", default=8000)
    URL_PREFIX: str = Field(description="URL to prefix routes on server", default="api")

    # ENTRY POINTS
    API_URL: str = Field(description="Server api URL", default="http://localhost:8080")

    # ADAPTERS
    SERVICE_NAME: str = Field(description="Service name", default="ALM backend alert")
    LOG_LEVEL: str = Field(
        description="Python Logging level. Must be a string like 'DEBUG' or 'Error'.", default="INFO"
    )

    # External APIs
    SITE_METRICS_URL: str = Field(description="Site metrics url")

    class Config:
        """Override env file, used in dev."""

        env_file = ".env"


config = Config()
