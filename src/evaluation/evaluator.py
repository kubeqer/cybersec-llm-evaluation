import re
from typing import Any
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict
from src.evaluation.schema import EvalResult, ConfusionMatrix
from src.llm.schema import EvalType


class LLMEvaluator:
    def __init__(
            self,
            llm_model: Any,
            eval_type: EvalType,
    ):
        self.llm_model = llm_model
        self.eval_type = eval_type
        logger.info(f"Initialized LLMEvaluator with eval_type={eval_type.value}")

    @log_calls(level="INFO", show_result=True)
    @error_handling(default=None, reraise=True)
    def evaluate(
            self, data: list[InputAnswerDict], max_samples: int | None = None
    ) -> EvalResult | None:
        if not data:
            logger.warning("Empty data provided for evaluation")
            return None

        eval_data = self._prepare_data(data, max_samples)
        confusion_matrix = self._evaluate_samples(eval_data)
        eval_result = self._build_result(eval_data, confusion_matrix)

        logger.info(
            f"Evaluation complete: {eval_result.correct}/{eval_result.total} correct ({eval_result.avg_comprehensiveness:.2f}%)\n"
            f"  TP={eval_result.true_positives}, FP={eval_result.false_positives}, "
            f"TN={eval_result.true_negatives}, FN={eval_result.false_negatives}\n"
            f"  Precision={eval_result.precision:.2f}%, Recall={eval_result.recall:.2f}%, F1={eval_result.f1_score:.2f}%"
        )

        return eval_result

    @staticmethod
    def _prepare_data(
            data: list[InputAnswerDict], max_samples: int | None
    ) -> list[InputAnswerDict]:
        eval_data = data[:max_samples] if max_samples else data
        logger.info(f"Evaluating {len(eval_data)} samples")
        return eval_data

    def _evaluate_samples(self, eval_data: list[InputAnswerDict]) -> ConfusionMatrix:
        confusion_matrix = ConfusionMatrix()
        for idx, item in enumerate(eval_data):
            predicted, actual = self._evaluate_single_sample(item, idx)
            if predicted == -1:
                confusion_matrix.false_negatives += 1
            else:
                confusion_matrix.update(predicted, actual)
            if (idx + 1) % 10 == 0:
                logger.info(f"Evaluated {idx + 1}/{len(eval_data)} samples")

        return confusion_matrix

    def _evaluate_single_sample(
            self, item: InputAnswerDict, idx: int
    ) -> tuple[int, int]:
        input_text: str = item["input"]
        expected_answer: int | str = item["answer"]
        actual_output = self.llm_model.generate(
            message=input_text, eval_type=self.eval_type
        )
        predicted = self._normalize_output(actual_output)
        actual = self._normalize_output(expected_answer)
        if predicted == -1:
            logger.warning(f"Invalid prediction at sample {idx + 1}: {actual_output}")
        return predicted, actual

    def _build_result(
            self, eval_data: list[InputAnswerDict], confusion_matrix: ConfusionMatrix
    ) -> EvalResult:
        total = len(eval_data)
        accuracy = self._calculate_accuracy(confusion_matrix)
        precision = self._calculate_precision(confusion_matrix)
        recall = self._calculate_recall(confusion_matrix)
        f1_score = self._calculate_f1_score(precision, recall)
        return EvalResult(
            model_name=self._get_model_name(),
            total=total,
            correct=confusion_matrix.correct,
            incorrect=confusion_matrix.incorrect,
            avg_comprehensiveness=accuracy,
            true_positives=confusion_matrix.true_positives,
            false_positives=confusion_matrix.false_positives,
            true_negatives=confusion_matrix.true_negatives,
            false_negatives=confusion_matrix.false_negatives,
            precision=precision * 100,
            recall=recall * 100,
            f1_score=f1_score * 100,
        )

    @staticmethod
    def _calculate_accuracy(confusion_matrix: ConfusionMatrix) -> float:
        denominator = confusion_matrix.correct + confusion_matrix.incorrect
        if denominator == 0:
            return 0.0
        return confusion_matrix.correct / denominator

    @staticmethod
    def _calculate_precision(confusion_matrix: ConfusionMatrix) -> float:
        denominator = confusion_matrix.true_positives + confusion_matrix.false_positives
        if denominator == 0:
            return 0.0
        return confusion_matrix.true_positives / denominator

    @staticmethod
    def _calculate_recall(confusion_matrix: ConfusionMatrix) -> float:
        denominator = confusion_matrix.true_positives + confusion_matrix.false_negatives
        if denominator == 0:
            return 0.0
        return confusion_matrix.true_positives / denominator

    @staticmethod
    def _calculate_f1_score(precision: float, recall: float) -> float:
        denominator = precision + recall
        if denominator == 0:
            return 0.0
        return 2 * precision * recall / denominator

    @staticmethod
    def _normalize_output(output: int | str) -> int:
        try:
            output_str = str(output).strip()
            if not output_str:
                logger.warning(f"Empty output")
                return -1
            final_answer_match = re.search(
                r'FINAL\s+ANSWER\s*:\s*([A-Da-d01])',
                output_str,
                re.IGNORECASE
            )
            if final_answer_match:
                char = final_answer_match.group(1).upper()
                if char in ('A', 'B', 'C', 'D'):
                    return ord(char) - ord('A')
                return int(char)
            answer_pattern = re.search(
                r'(?:answer is|答案是|答案：)\s*([A-Da-d])',
                output_str,
                re.IGNORECASE
            )
            if answer_pattern:
                letter = answer_pattern.group(1).upper()
                return ord(letter) - ord('A')
            boxed_match = re.search(r'\{([A-Da-d01])}', output_str)
            if boxed_match:
                char = boxed_match.group(1).upper()
                if char in ('A', 'B', 'C', 'D'):
                    return ord(char) - ord('A')
                return int(char)
            first_char = output_str[0].upper()
            if first_char in ('A', 'B', 'C', 'D'):
                return ord(first_char) - ord('A')
            if first_char in ('0', '1'):
                return int(first_char)
            colon_match = re.search(r':\s*([01])', output_str)
            if colon_match:
                return int(colon_match.group(1))
            letter_match = re.search(r'\b([A-Da-d])\b', output_str)
            if letter_match:
                letter = letter_match.group(1).upper()
                return ord(letter) - ord('A')
            digits = re.findall(r'\b([01])\b', output_str)
            if digits:
                return int(digits[0])
            output_lower = output_str.lower()
            if 'zero' in output_lower or 'not vulnerable' in output_lower or 'not phishing' in output_lower or 'safe' in output_lower or 'legitimate' in output_lower:
                return 0
            if 'one' in output_lower or 'vulnerable' in output_lower or 'phishing' in output_lower or 'malicious' in output_lower:
                return 1
            numbers = re.findall(r'\d+', output_str)
            for num in numbers:
                val = int(num)
                if val in (0, 1, 2, 3):
                    return val
            logger.warning(f"Cannot parse output: {output_str[:100]}")
            return -1
        except (ValueError, TypeError, IndexError) as e:
            logger.warning(f"Error parsing output: {output} - {e}")
            return -1


    def _get_model_name(self) -> str:
        try:
            if hasattr(self.llm_model, "model_config"):
                return str(self.llm_model.model_config.model_name)
            return "unknown_model"
        except Exception:
            return "unknown_model"
