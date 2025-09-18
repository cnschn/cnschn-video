from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class BunnySettings(BaseSettings):
    api_key: str = Field(default=...)
    library_id: int = Field(default=...)
    public_collection_id: str = Field(default=...)
    pull_zone: str = Field(default=...)

    model_config = SettingsConfigDict(env_prefix='bunny_stream_')

bunny = BunnySettings()
