from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # mode
    use_mock_adapters: bool = True

    # database
    sqlite_path: str = "./daily_ops_agent.sqlite"

    # demo landing pages (comma-separated)
    # Use public pages that usually allow bots (demo-only)
    landing_pages: str = "https://example.com,https://httpbin.org/html,https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"


settings = Settings()
