from sqlmodel import Field, SQLModel

from web_app.models.base import SafeModel


class Embedding(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False)
    text: str = Field(index=True, nullable=False, unique=True)


class EmbeddingCreate(SafeModel):
    text: str
