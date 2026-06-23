from dataclasses import dataclass


@dataclass
class RankedItem:
    id: str
    document: str
    metadata: dict
    score: float = 0.0
    source: str = ""


def reciprocal_rank_fusion(
    ranked_lists: list[list[RankedItem]],
    k: int = 60,
) -> list[RankedItem]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF score = sum(1 / (k + rank_i)) across all lists where item appears.
    k=60 is the standard constant from the original RRF paper.
    """
    item_scores: dict[str, RankedItem] = {}
    item_rrf: dict[str, float] = {}

    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list, start=1):
            key = item.id
            if key not in item_scores:
                item_scores[key] = item
                item_rrf[key] = 0.0
            item_rrf[key] += 1.0 / (k + rank)

    fused = []
    for item_id, rrf_score in item_rrf.items():
        item = item_scores[item_id]
        item.score = rrf_score
        fused.append(item)

    fused.sort(key=lambda x: x.score, reverse=True)
    return fused
