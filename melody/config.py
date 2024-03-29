from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_uri: str = "sqlite://melody.db"
    conn_pool_min_size: int = 5
    conn_pool_max_size: int = 20


database_settings = DatabaseSettings()
