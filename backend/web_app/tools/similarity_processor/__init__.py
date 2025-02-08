import logging

import httpx
import jmespath
from tenacity import (
    RetryCallState,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
    wait_random,
)

from web_app.config import get_settings
from web_app.tools import RetryableException
from web_app.tools.requester import async_request_api

settings = get_settings()
logger = logging.getLogger(__name__)


def failed_get_embeddings(
    retry_state: RetryCallState,
) -> None:
    logger.error(
        f"Couldn't get search request embedding with "
        f"{retry_state.attempt_number} attemps ({round(retry_state.idle_for, 2)}s)."
    )
    return None


@retry(
    retry=retry_if_exception_type(RetryableException),
    stop=stop_after_attempt(5),
    wait=wait_fixed(1) + wait_random(0, 3),
    retry_error_callback=failed_get_embeddings,
)
async def get_embeddings(
    client: httpx.AsyncClient,
    embeddings_input: list[str],
    label: str = "",
) -> list[list[float]]:
    input_data: dict[str, str | list[str] | int] = {
        "input": embeddings_input,
        "model": settings.similarity_processor.OPENAI_EMBEDDINGS_MODEL,
    }
    dimensions = settings.similarity_processor.OPENAI_EMBEDDINGS_DIMENSIONS
    if dimensions:
        input_data["dimensions"] = dimensions
    response = await async_request_api(
        client=client,
        url=settings.similarity_processor.OPENAI_EMBEDDINGS_URL,
        method="POST",
        json_data=input_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.similarity_processor.OPENAI_API_KEY}",
        },
        label=f"{label} ({embeddings_input})",
    )
    embeddings = jmespath.search("data[].embedding", response)
    if not embeddings:
        raise RetryableException(
            f"Couldn't get embeddings for {label} ({embeddings_input}). Retrying."
        )
    if len(embeddings) != len(embeddings_input):
        raise RetryableException(
            f"Got {len(embeddings)} embeddings for {len(embeddings_input)} "
            f"inputs for {label} ({embeddings_input}). Retrying."
        )
    return embeddings
