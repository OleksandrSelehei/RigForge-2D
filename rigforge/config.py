"""Application configuration."""

from pathlib import Path

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

CONFIG_FILE = Path(__file__).resolve().parents[1] / "config.toml"


class RigForgeConfig(BaseSettings):
    """Runtime settings shared by the CLI and GUI front ends."""

    model_config = SettingsConfigDict(
        env_prefix="RIGFORGE_",
        toml_file=CONFIG_FILE,
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )


def load_config() -> RigForgeConfig:
    """Load settings from the environment and the TOML config file."""
    return RigForgeConfig()
