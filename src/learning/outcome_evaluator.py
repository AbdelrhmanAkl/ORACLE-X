class OutcomeEvaluator:
    """
    Deterministic evaluator for observed decision outcomes.
    """

    VERSION = "1.0"
    INVENTORY_COVER_THRESHOLD_DAYS = 10.0

    def evaluate_inventory_cover(self, inventory_cover_days):
        if inventory_cover_days is None:
            return {
                "outcome_class": "INCONCLUSIVE_OUTCOME",
                "metric": "inventory_cover_days",
                "value": None,
                "threshold": self.INVENTORY_COVER_THRESHOLD_DAYS,
                "provenance": "OBSERVED_OUTCOME",
            }

        if inventory_cover_days >= self.INVENTORY_COVER_THRESHOLD_DAYS:
            outcome_class = "POSITIVE_OUTCOME"
        else:
            outcome_class = "NEGATIVE_OUTCOME"

        return {
            "outcome_class": outcome_class,
            "metric": "inventory_cover_days",
            "value": inventory_cover_days,
            "threshold": self.INVENTORY_COVER_THRESHOLD_DAYS,
            "provenance": "OBSERVED_OUTCOME",
        }