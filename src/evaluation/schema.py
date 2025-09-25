from dataclasses import dataclass


@dataclass
class EvalResult:
    model_name: str
    total: int
    correct: int
    incorrect: int
    avg_comprehensiveness: float
