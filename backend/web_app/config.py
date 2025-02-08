import logging
import os
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SimilarityProcessorSettings:
    OPENAI_API_KEY: str
    OPENAI_EMBEDDINGS_URL: str
    OPENAI_EMBEDDINGS_MODEL: str
    OPENAI_EMBEDDINGS_DIMENSIONS: int | None = None


@dataclass(frozen=True)
class Settings:
    similarity_processor: SimilarityProcessorSettings = SimilarityProcessorSettings(
        OPENAI_API_KEY=os.environ["OPENAI_API_KEY"],
        OPENAI_EMBEDDINGS_URL="https://api.openai.com/v1/embeddings",
        OPENAI_EMBEDDINGS_MODEL="text-embedding-3-large",
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Prepare and cache web_app settings.
    """
    return Settings()
