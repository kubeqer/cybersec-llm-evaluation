from dataclasses import dataclass


@dataclass
class EvalResult:
    model_name: str
    total: int
    correct: int
    incorrect: int
    avg_comprehensiveness: float
    true_positives: int
    false_positives: int
    true_negatives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float


@dataclass
class ConfusionMatrix:
    true_positives: int = 0
    false_positives: int = 0
    true_negatives: int = 0
    false_negatives: int = 0

    def update(self, predicted: int, actual: int, is_multiclass: bool = False) -> None:
        if is_multiclass:
            if predicted == actual:
                self.true_positives += 1
            else:
                self.false_negatives += 1
        else:
            if predicted == 1 and actual == 1:
                self.true_positives += 1
            elif predicted == 1 and actual == 0:
                self.false_positives += 1
            elif predicted == 0 and actual == 0:
                self.true_negatives += 1
            elif predicted == 0 and actual == 1:
                self.false_negatives += 1

    @property
    def correct(self) -> int:
        return self.true_positives + self.true_negatives

    @property
    def incorrect(self) -> int:
        return self.false_positives + self.false_negatives