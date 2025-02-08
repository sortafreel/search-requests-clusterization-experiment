import logging
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CustomSettings:
    CUSTOM_SUB_SETTING: str


@dataclass(frozen=True)
class Settings:
    CUSTOM_SETTING: int = 42
    custom_set_of_settings: CustomSettings = CustomSettings(
        CUSTOM_SUB_SETTING="sub_setting"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Prepare and cache web_app settings.
    """
    return Settings()
