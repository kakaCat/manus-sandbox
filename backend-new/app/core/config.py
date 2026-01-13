from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM Configuration
    openai_api_key: str = ""
    openai_api_base: str = "https://api.deepseek.com/v1"
    model_name: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 4000

    # MongoDB Configuration
    mongodb_uri: str = "mongodb://mongodb:27017"
    mongodb_database: str = "manus"
    mongodb_username: str | None = None
    mongodb_password: str | None = None

    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Sandbox Configuration
    sandbox_address: str | None = None
    sandbox_image: str = "simpleyyt/manus-sandbox"
    sandbox_name_prefix: str = "sandbox"
    sandbox_ttl_minutes: int = 30
    sandbox_network: str = "manus-network"
    sandbox_chrome_args: str = ""

    # Search Configuration
    search_provider: str = "bing"  # bing, google, baidu
    google_search_api_key: str | None = None
    google_search_engine_id: str | None = None

    # Auth Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    auth_provider: str = "none"  # none, password, local

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def validate(self):
    
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")


@lru_cache()
def get_settings() -> Settings:

    settings = Settings()
    settings.validate()
    return settings
