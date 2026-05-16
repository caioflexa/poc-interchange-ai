class ConfidenceScoring:
    # Sistema de pontuação para medir a confiabilidade da extração
    @staticmethod
    def calculate(extraction_method: str, has_all_fields: bool) -> float:
        # Define pesos para cada método e penaliza campos ausentes
        base_scores = {
            "regex": 0.6,
            "table_parser": 0.8,
            "llm": 0.85,
            "manual_seed": 1.0,
            "mock": 0.5,
        }
        score = base_scores.get(extraction_method, 0.4)
        if not has_all_fields:
            score -= 0.2
        return max(0.1, score)
