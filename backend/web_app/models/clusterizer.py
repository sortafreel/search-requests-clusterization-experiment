from dataclasses import dataclass

from pydantic import Field, field_validator

from web_app.models.base import SafeModel


@dataclass(frozen=True)
class PhrasesGroup:
    phrases: list[str]
    avg_distance: float | None


@dataclass(frozen=True)
class PhrasesCluster:
    phrases: list[str]
    embeddings: list[list[float]]


class PhrasesInput(SafeModel):
    phrases: list[str]

    # noinspection PyNestedDecorators
    @field_validator("phrases", mode="after")
    @classmethod
    def validate_phrases(cls, values: list[str]) -> list[str]:
        for value in values:
            if len(value) < 1 or len(value) > 1000:
                raise ValueError(
                    f"Only phrases from 1 to 1000 symbols are allowed, "
                    f'got {len(value)} sumbols: "{value}".'
                )
        return values

    @property
    def unique_phrases(self) -> list[str]:
        """
        Make sure to get only unique phrases (strip/lower), to process each one only once
        :return: Unique phrases, keeping the order.
        """
        return list(dict.fromkeys([x.strip().lower() for x in self.phrases]))

    @property
    def sorted_unique_phrases(self) -> list[str]:
        """
        :return: Unique phrases, sorted alphabetically.
        """
        return sorted(self.unique_phrases)


class GroupingPhrasesInput(PhrasesInput):
    phrases: list[str] = Field(
        ...,
        description="Phrases to group.",
        min_length=1,
        max_length=8000,
    )


class GroupingPhrasesOutput(SafeModel):
    groups: dict[str, PhrasesGroup] = Field(
        ...,
        description="Grouped phrases.",
        min_length=0,
        max_length=8000,
    )
    singles: list[str] = Field(
        ...,
        description="Phrases that weren't grouped.",
        min_length=0,
        max_length=8000,
    )
