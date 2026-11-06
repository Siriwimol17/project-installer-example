"""Environment-backed service configuration."""

from dataclasses import dataclass
import os
from pathlib import Path


class ConfigError(ValueError):
    """Raised when required service configuration is invalid."""


@dataclass(frozen=True)
class Settings:
    port: int
    internal_token: str
    data_dir: Path
    service_name: str = "py-svc"

    @classmethod
    def from_env(cls) -> "Settings":
        port_value = os.getenv("PORT")
        token = os.getenv("INTERNAL_TOKEN")
        data_dir_value = os.getenv("DATA_DIR")

        try:
            port = int(port_value) if port_value is not None else 0
        except ValueError as exc:
            raise ConfigError("PORT is required and must be a valid port (1-65535).") from exc
        if not 1 <= port <= 65535:
            raise ConfigError("PORT is required and must be a valid port (1-65535).")
        if token is None or not token.strip():
            raise ConfigError("INTERNAL_TOKEN is required.")
        if data_dir_value is None or not data_dir_value.strip():
            raise ConfigError("DATA_DIR is required.")

        data_dir = Path(data_dir_value)
        data_dir.mkdir(parents=True, exist_ok=True)
        return cls(port=port, internal_token=token, data_dir=data_dir)
