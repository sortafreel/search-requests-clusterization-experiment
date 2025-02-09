import logging
import os
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SimilarityProcessorSettings:
    OPENAI_API_KEY: str
    OPENAI_EMBEDDINGS_URL: str = "https://api.openai.com/v1/embeddings"
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-3-large"
    OPENAI_EMBEDDINGS_TIMEOUT: int = 15
    OPENAI_EMBEDDINGS_DIMENSIONS: int | None = None


@dataclass(frozen=True)
class CluterizerSettings:
    # How many embeddings to process at once, when grouping suggestions
    EMBEDDINGS_CHUNK_SIZE: int = 1000
    # Expected average distance between embeddings to group them
    EMBEDDINGS_CLUSTERING_DISTANCE: float = 0.95
    # How many times to try to group until to stop
    EMBEDDINGS_CLUSTERING_ITERATIONS: int = 6
    # How many times max to re-group singles to increase group count
    EMBEDDINGS_CLUSTERING_MAX_RECURSION: int = 3
    # How many additional recursions allowed if the tail is too large (loose suggestions)
    EMBEDDINGS_CLUSTERING_MAX_TAIL_RECURSION: int = 3
    # How to decrease the distance between embeddings to group them with each iteration,
    # to increase the number of groups and improve the user experience
    EMBEDDINGS_CLUSTERING_DISTANCE_DECREASE: float = 0.01
    # How many times to try to group when trying to decrease the tail (too large, loose suggestions)
    EMBEDDINGS_CLUSTERING_MAX_TAIL_ITERATIONS: int = 1
    # Split embeddings into chunks to speed up clustering
    EMBEDDINGS_CLUSTERING_CHUNK_SIZE: int = 25
    # Expected suggestions per group when grouping embeddings
    SUGGESTIONS_PER_EMBEDDINGS_GROUP: int = 5
    # Max suggestions per group to avoid large loosely-related groups
    MAX_SUGGESTIONS_PER_EMBEDDINGS_GROUP: int = 10
    # If the tail is larger than that - try to cluster once more with more loose approach
    EMBEDDINGS_CLUSTERING_MAX_TAIL_PERCENTAGE: float = 0.50


@dataclass(frozen=True)
class Settings:
    similarity_processor: SimilarityProcessorSettings = SimilarityProcessorSettings(
        OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]
    )
    clusterizer: CluterizerSettings = CluterizerSettings()


@lru_cache()
def get_settings() -> Settings:
    """
    Prepare and cache web_app settings.
    """
    return Settings()
