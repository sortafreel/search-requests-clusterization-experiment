import asyncio
import logging
import math

import httpx
import numpy as np
import shortuuid
from sklearn.cluster import KMeans, MiniBatchKMeans
from tqdm.asyncio import tqdm

from web_app.config import get_settings
from web_app.models.clusterizer import SuggestionsCluster, SuggestionsGroup
from web_app.tools.clusterizer.utils import cosine_similarity, str_chunks
from web_app.tools.similarity_processor import get_embeddings

logger = logging.getLogger(__name__)
settings = get_settings()


class Clusterizer:
    @staticmethod
    async def _get_suggestions_chunk_embeddings(
        client: httpx.AsyncClient,
        embeddings_input: list[str],
    ) -> tuple[list[str], list[list[float]]]:
        suggestions_embeddings = await get_embeddings(
            client=client,
            embeddings_input=embeddings_input,
            settings=settings,
            label="suggestions embeddings",
        )
        return embeddings_input, suggestions_embeddings

    @classmethod
    async def get_all_suggestions_embeddings(
        cls,
        suggestions_input: list[str],
    ) -> tuple[list[str], list[list[float]]]:
        asyncio_tasks = []
        suggestions = []
        embeddings = []
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                settings.similarity_processor.OPENAI_EMBEDDINGS_TIMEOUT, pool=None
            ),
        ) as client:
            # Chunk embeddings to avoid hitting the API limit
            for chunk in str_chunks(
                suggestions_input,
                settings.clusterizer.EMBEDDINGS_CHUNK_SIZE,
            ):
                asyncio_tasks.append(
                    cls._get_suggestions_chunk_embeddings(
                        client=client, embeddings_input=chunk
                    )
                )
            for st in tqdm(
                asyncio.as_completed(asyncio_tasks),
                total=len(asyncio_tasks),
                desc="Getting suggestions embeddings",
            ):
                suggestions_part, embeddings_part = await st
                suggestions += suggestions_part
                embeddings += embeddings_part
        return suggestions, embeddings

    @classmethod
    def clusterize_suggestions(
        cls,
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        max_tail_size: int,
        pre_combined_groups: dict[str, SuggestionsGroup] | None = None,
        iteration: int = 0,
    ) -> tuple[dict[str, SuggestionsGroup], SuggestionsCluster]:
        """
        Wrapper for clusterizing suggestions, to allow tracking stats
        for clusterization iterations only once, on final iteration.
        """
        # Assuming the input is sorted alphabetically in hope to improve grouping quality
        # TODO Sort it when processing the input?
        return cls._clusterize_suggestions(
            embedded_suggestions=embedded_suggestions,
            embeddings=embeddings,
            max_tail_size=max_tail_size,
            pre_combined_groups=pre_combined_groups,
            iteration=iteration,
        )

    @staticmethod
    def sort_relevant_groups(
        relevant_groups: dict[str, SuggestionsGroup],
    ) -> dict[str, SuggestionsGroup]:
        # Sort relevant groups by the average distance, keep the groups with the best distance first
        return dict(
            sorted(  # type: ignore
                relevant_groups.items(),
                key=lambda item: item[1].avg_distance,  # type: ignore
                reverse=True,
            )
        )

    @classmethod
    def _clusterize_suggestions_iteration(
        cls,
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        iteration: int,
        clustering_distance: float,
        clustering_iterations: int,
    ) -> tuple[list[dict[str, SuggestionsGroup]], list[SuggestionsCluster]]:
        # Split suggestions into smaller groups based on embeddings
        n_clusters = math.ceil(
            len(embeddings) / settings.clusterizer.EMBEDDINGS_CLUSTERING_CHUNK_SIZE
        )
        if n_clusters == 1:
            # If it's a single cluster - create it manually
            init_embeddings_clusters = {
                "single_cluster": SuggestionsCluster(
                    suggestions=embedded_suggestions, embeddings=embeddings
                )
            }
        else:
            init_embeddings_clusters = cls._calculate_embeddings_clusters(
                embedded_suggestions=embedded_suggestions,
                embeddings=embeddings,
                n_clusters=n_clusters,
                minibatch=True,
            )
        return cls._group_multiple_embeddings_clusters(
            init_embeddings_clusters=init_embeddings_clusters,
            iteration=iteration,
            clustering_distance=clustering_distance,
            clustering_iterations=clustering_iterations,
        )

    @classmethod
    def _group_multiple_embeddings_clusters(
        cls,
        init_embeddings_clusters: dict[str, SuggestionsCluster],
        iteration: int,
        clustering_distance: float,
        clustering_iterations: int,
    ) -> tuple[list[dict[str, SuggestionsGroup]], list[SuggestionsCluster]]:
        groups = []
        singles = []
        # Find groups of suggestions in each cluster, one by one
        for i, (_, cluster) in enumerate(
            tqdm(
                init_embeddings_clusters.items(),
                desc=f"Grouping embeddings clusters (iteration: {iteration})",
            )
        ):
            cluster_groups, cluster_singles = cls._group_embeddings_cluster(
                embedded_suggestions=cluster.suggestions,
                embeddings=cluster.embeddings,
                clustering_distance=clustering_distance,
                clustering_iterations=clustering_iterations,
            )
            groups.append(cluster_groups)
            singles.append(cluster_singles)
        return groups, singles

    @classmethod
    def _clusterize_suggestions(
        cls,
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        max_tail_size: int,
        pre_combined_groups: dict[str, SuggestionsGroup] | None,
        iteration: int,
        clustering_distance: float = settings.clusterizer.EMBEDDINGS_CLUSTERING_DISTANCE,
        clustering_iterations: int = settings.clusterizer.EMBEDDINGS_CLUSTERING_ITERATIONS,
    ) -> tuple[dict[str, SuggestionsGroup], SuggestionsCluster]:
        groups, singles = cls._clusterize_suggestions_iteration(
            embedded_suggestions=embedded_suggestions,
            embeddings=embeddings,
            iteration=iteration,
            clustering_distance=clustering_distance,
            clustering_iterations=clustering_iterations,
        )
        combined_groups: dict[str, SuggestionsGroup] = {}
        # If pre-combined groups are provided - add them to the combined groups
        if pre_combined_groups:
            groups = [pre_combined_groups] + groups
        for group_set in groups:
            combined_groups = {**combined_groups, **group_set}
        # Combine the singles in the expected format
        combined_singles = SuggestionsCluster(suggestions=[], embeddings=[])
        for single in singles:
            combined_singles.suggestions.extend(single.suggestions)
            combined_singles.embeddings.extend(single.embeddings)
        # If there are still iterations left - iterate again
        if iteration < settings.clusterizer.EMBEDDINGS_CLUSTERING_MAX_RECURSION:
            return cls._clusterize_suggestions(
                embedded_suggestions=combined_singles.suggestions,
                embeddings=combined_singles.embeddings,
                max_tail_size=max_tail_size,
                pre_combined_groups=combined_groups,
                iteration=iteration + 1,
            )
        # If the iterations exhausted and the tail is acceptable - return the results
        if len(combined_singles.suggestions) <= max_tail_size:
            return combined_groups, combined_singles
        # If the tail is still too large, but no max tail recursions left - return the results anyway
        if iteration >= (
            settings.clusterizer.EMBEDDINGS_CLUSTERING_MAX_RECURSION
            + settings.clusterizer.EMBEDDINGS_CLUSTERING_MAX_TAIL_RECURSION
        ):
            return combined_groups, combined_singles
        # If the tail is still too large and there are max tail recursions left -
        # iterate again with the lowest allowed average distance
        max_tail_clustering_distance = round(
            (
                # Calculate the lowest allowed distance
                settings.clusterizer.EMBEDDINGS_CLUSTERING_DISTANCE
                - (
                    # First iteration doesn't count (i-0), so decrease the distance by 1
                    (settings.clusterizer.EMBEDDINGS_CLUSTERING_ITERATIONS - 1)
                    * settings.clusterizer.EMBEDDINGS_CLUSTERING_DISTANCE_DECREASE
                )
            ),
            2,
        )
        return cls._clusterize_suggestions(
            embedded_suggestions=combined_singles.suggestions,
            embeddings=combined_singles.embeddings,
            max_tail_size=max_tail_size,
            pre_combined_groups=combined_groups,
            iteration=iteration + 1,
            clustering_distance=max_tail_clustering_distance,
            clustering_iterations=settings.clusterizer.EMBEDDINGS_CLUSTERING_MAX_TAIL_ITERATIONS,
        )

    @classmethod
    def _group_embeddings_cluster(
        cls,
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        clustering_distance: float,
        clustering_iterations: int,
    ) -> tuple[dict[str, SuggestionsGroup], SuggestionsCluster]:
        # Define result variables to update with each iteration
        result_relevant_groups: dict[str, SuggestionsGroup] = {}
        result_singles: SuggestionsCluster = SuggestionsCluster(
            suggestions=[], embeddings=[]
        )
        suggestions_input, embeddings_input = embedded_suggestions, embeddings
        # An expected average of suggestions per group.
        embeddings_per_group = settings.clusterizer.SUGGESTIONS_PER_EMBEDDINGS_GROUP
        # How many times to clusterize until to stop (to disallow while loop to run forever)
        # Decrease the required distance (- quality) and decrease the cluster size (+ quality) with each iteration
        for distance_iteration in range(clustering_iterations):
            n_clusters = math.ceil(len(suggestions_input) / embeddings_per_group)
            # Decrease required distance to group embeddings with each iteration,
            # to allow more ideas to be grouped and improve the user experience
            avg_distance_threshold = round(
                clustering_distance
                - (
                    settings.clusterizer.EMBEDDINGS_CLUSTERING_DISTANCE_DECREASE
                    * distance_iteration
                ),
                2,
            )
            (
                relevant_groups,
                result_singles,
            ) = cls._group_embeddings_cluster_iteration(
                embedded_suggestions=suggestions_input,
                embeddings=embeddings_input,
                n_clusters=n_clusters,
                avg_distance_threshold=avg_distance_threshold,
            )
            # Save successfully groupped suggestions
            result_relevant_groups = {**result_relevant_groups, **relevant_groups}
            # If no singles left - nothing to group again, return results
            if not result_singles.suggestions:
                return result_relevant_groups, result_singles
            # If singles left, but less than a single group - don't group them again
            if len(result_singles.suggestions) < embeddings_per_group:
                return result_relevant_groups, result_singles
            # If enough singles left - try to clusterize them again
            suggestions_input, embeddings_input = (
                result_singles.suggestions,
                result_singles.embeddings,
            )
        # Return the final results
        return result_relevant_groups, result_singles

    @staticmethod
    def _calculate_embeddings_clusters(
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        n_clusters: int,
        minibatch: bool,
    ) -> dict[str, SuggestionsCluster]:
        matrix = np.vstack(embeddings)
        if not minibatch:
            kmeans = KMeans(
                n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42
            )
        else:
            kmeans = MiniBatchKMeans(
                n_clusters=n_clusters, init="k-means++", n_init=10, random_state=42
            )
        kmeans.fit_predict(matrix)
        labels: list[int] = kmeans.labels_
        # Organize clustered suggestions
        grouped_suggestions: dict[str, SuggestionsCluster] = {}
        # Generate unique label for each clustering calculation
        unique_label = str(shortuuid.ShortUUID().random(length=8))
        for suggestion, label, emb in zip(embedded_suggestions, labels, embeddings):
            formatted_label = f"{label}_{unique_label}"
            if formatted_label not in grouped_suggestions:
                grouped_suggestions[formatted_label] = SuggestionsCluster(
                    suggestions=[], embeddings=[]
                )
            grouped_suggestions[formatted_label].suggestions.append(suggestion)
            grouped_suggestions[formatted_label].embeddings.append(emb)
        return grouped_suggestions

    @classmethod
    def _group_embeddings_cluster_iteration(
        cls,
        embedded_suggestions: list[str],
        embeddings: list[list[float]],
        n_clusters: int,
        avg_distance_threshold: float | None,
    ) -> tuple[dict[str, SuggestionsGroup], SuggestionsCluster]:
        embeddings_clusters = cls._calculate_embeddings_clusters(
            embedded_suggestions=embedded_suggestions,
            embeddings=embeddings,
            n_clusters=n_clusters,
            minibatch=False,
        )
        # Split into relevant groups and singles
        relevant_groups: dict[str, SuggestionsGroup] = {}
        singles = SuggestionsCluster(suggestions=[], embeddings=[])
        for group_label, cluster in embeddings_clusters.items():
            if len(cluster.suggestions) <= 1:
                # Groups with a single idea move to singles automatically
                singles.suggestions.extend(cluster.suggestions)
                singles.embeddings.extend(cluster.embeddings)
                continue
            # If avg distance threshold not provided (init chunking) - don't filter groups
            if not avg_distance_threshold:
                # Keep the proper-sized groups that are close to each other
                relevant_groups[group_label] = SuggestionsGroup(
                    suggestions=cluster.suggestions,
                    avg_distance=None,
                )
                continue
            # Calculate average distance between all suggestions in the group
            distances = []
            for suggestion, emb in zip(cluster.suggestions, cluster.embeddings):
                for l_suggestion, l_emb in zip(cluster.suggestions, cluster.embeddings):
                    if suggestion != l_suggestion:
                        distances.append(cosine_similarity(emb, l_emb))
            # Round to 2 symbols after the dot
            avg_distance = round(sum(distances) / len(distances), 2)
            # Groups that aren't close enough move to singles
            if avg_distance < avg_distance_threshold:
                singles.suggestions.extend(cluster.suggestions)
                singles.embeddings.extend(cluster.embeddings)
                continue
            # Avoid having large loosely-connected groups
            if (
                len(cluster.suggestions)
                > settings.clusterizer.MAX_SUGGESTIONS_PER_EMBEDDINGS_GROUP
            ):
                singles.suggestions.extend(cluster.suggestions)
                singles.embeddings.extend(cluster.embeddings)
                continue
            # Keep the proper-sized groups that are close to each other
            relevant_groups[group_label] = SuggestionsGroup(
                # Don't save embeddings, as the group is already relevant,
                # so won't go through the clusterization again
                suggestions=cluster.suggestions,
                avg_distance=avg_distance,
            )
        return relevant_groups, singles
