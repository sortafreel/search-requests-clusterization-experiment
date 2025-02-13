from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from web_app.models.embeddings import Embedding, EmbeddingCreate


async def get_embeddings_service() -> "EmbeddingsService":
    return EmbeddingsService()


class EmbeddingsService:

    @staticmethod
    async def add_embedding(session: AsyncSession, embedding: EmbeddingCreate) -> None:
        # Check if the embedding already exists
        query = select(Embedding).where(Embedding.text == embedding.text)
        result = await session.exec(query)
        existing_embedding = result.first()
        if existing_embedding:
            return
        # Store if not
        db_embedding = Embedding(**embedding.model_dump())
        session.add(db_embedding)
        await session.commit()
        return
