from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "Aottar AI"
    APP_VERSION: str = "1.0"

    GROQ_API_KEY: str

    # WooCommerce
    WC_URL: str
    WC_CONSUMER_KEY: str
    WC_CONSUMER_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()