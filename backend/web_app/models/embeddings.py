from sqlmodel import Field, SQLModel

from web_app.models.base import SafeModel


class Embedding(SQLModel, table=True):
    id: int = Field(primary_key=True, nullable=False)
    text: str = Field(index=True, nullable=False, unique=True)
    # Sample embedding field, later replace with pgvector field
    embedding: str = Field(nullable=False)


class EmbeddingCreate(SafeModel):
    text: str
