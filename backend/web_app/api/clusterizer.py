import logging

from fastapi import APIRouter
from starlette.responses import JSONResponse

from web_app.config import get_settings
from web_app.models.clusterizer import GroupingPhrasesInput
from web_app.tools.clusterizer import Clusterizer

router = APIRouter(prefix="/clusterizer")
logger = logging.getLogger(__name__)
settings = get_settings()


@router.post(
    "/group/",
    response_description="Group phrases.",
)
async def group_phrases(phrases_to_group: GroupingPhrasesInput) -> JSONResponse:
    """
    Combine chunks of suggestions from Redis, and try to group remaining singles.
    """
    # Organize all suggestions into groups
    # TODO Add chunking if too many singles left?
    (
        embedded_phrases,
        embeddings,
    ) = await Clusterizer.get_all_phrases_embeddings(
        phrases_input=phrases_to_group.sorted_unique_phrases
    )
    groups, singles = Clusterizer.clusterize_phrases(
        embedded_phrases=embedded_phrases,
        embeddings=embeddings,
        max_tail_size=int(
            len(embeddings)
            * settings.clusterizer.EMBEDDINGS_CLUSTERING_MAX_TAIL_PERCENTAGE
        ),
    )
    # Return success
    return JSONResponse(status_code=200, content={"status": "success"})
