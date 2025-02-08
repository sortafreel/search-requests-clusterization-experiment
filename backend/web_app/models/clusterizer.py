from dataclasses import dataclass


@dataclass(frozen=True)
class SuggestionsGroup:
    suggestions: list[str]
    avg_distance: float | None


@dataclass(frozen=True)
class SuggestionsCluster:
    suggestions: list[str]
    embeddings: list[list[float]]
