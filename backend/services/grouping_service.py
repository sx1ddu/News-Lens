"""
Groups analyzed articles by the two independent classification dimensions.

Bias grouping and stance grouping are computed separately and never mixed -
an article's bias group and stance group are two different facts about it.
"""

BIAS_GROUP_KEYS = {
    "Left": "left",
    "Center": "center",
    "Right": "right",
}

STANCE_GROUP_KEYS = {
    "Supports": "supports",
    "Neutral": "neutral",
    "Questions / Critical": "critical",
}


class GroupingService:
    def group_by_bias(self, articles: list[dict]) -> dict:
        groups = {key: [] for key in BIAS_GROUP_KEYS.values()}

        for article in articles:
            label = article["bias"]["label"]
            group_key = BIAS_GROUP_KEYS.get(label)
            if group_key:
                groups[group_key].append(article)

        return groups

    def group_by_stance(self, articles: list[dict]) -> dict:
        groups = {key: [] for key in STANCE_GROUP_KEYS.values()}

        for article in articles:
            stance = article.get("stance")
            if not stance:
                continue

            group_key = STANCE_GROUP_KEYS.get(stance["label"])
            if group_key:
                groups[group_key].append(article)

        return groups


grouping_service = GroupingService()
