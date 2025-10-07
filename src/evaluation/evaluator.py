from typing import Any

from deepeval import evaluate
from deepeval.metrics import DAGMetric
from deepeval.metrics.dag import BinaryJudgementNode, VerdictNode, DeepAcyclicGraph
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict
from src.evaluation.schema import EvalResult
from src.llm.schema import EvalType


class LLMEvaluator:
    def __init__(
            self,
            llm_model: Any,
            eval_type: EvalType,
            threshold: float = 0.5,
    ):
        self.llm_model = llm_model
        self.eval_type = eval_type
        self.threshold = threshold
        logger.info(
            f"Initialized LLMEvaluator with eval_type={eval_type.value}, "
            f"threshold={threshold}"
        )

    @log_calls(level="INFO", show_result=True)
    @error_handling(default=None, reraise=True)
    def evaluate(
            self, data: list[InputAnswerDict], max_samples: int | None = None
    ) -> EvalResult:
        if not data:
            logger.warning("Empty data provided for evaluation")
            return EvalResult(
                model_name=self._get_model_name(),
                total=0,
                correct=0,
                incorrect=0,
                avg_comprehensiveness=0.0,
            )
        eval_data = data[:max_samples] if max_samples else data
        logger.info(f"Evaluating {len(eval_data)} samples")
        test_cases = self._create_test_cases(eval_data)
        root_node = BinaryJudgementNode(
            criteria="Does the actual output match the expected output? Consider semantic equivalence (e.g., 'yes' = 'true', '1' = 'positive', 'no' = 'false', '0' = 'negative').",
            children=[
                VerdictNode(verdict=True, score=1),
                VerdictNode(verdict=False, score=0)
            ],
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT
            ],
            label="Check Binary Match"
        )
        dag = DeepAcyclicGraph(root_nodes=[root_node]) # type: ignore[arg-type]
        metric = DAGMetric(
            name="Binary Accuracy",
            dag=dag,
            threshold=self.threshold
        )
        logger.info("Running DeepEval evaluation.")
        results = evaluate(test_cases=test_cases, metrics=[metric]) # type: ignore[arg-type]
        return self._aggregate_results(results, len(eval_data))

    def _create_test_cases(self, data: list[InputAnswerDict]) -> list[LLMTestCase]:
        test_cases = []
        for idx, item in enumerate(data):
            input_text: str = item["input"]
            expected_answer: int | str = item["answer"]
            actual_output = self.llm_model.generate(
                message=input_text, eval_type=self.eval_type
            )
            test_case = LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=str(expected_answer),
            )
            test_cases.append(test_case)
            if (idx + 1) % 10 == 0:
                logger.info(f"Created {idx + 1}/{len(data)} test cases")
        return test_cases

    def _aggregate_results(
            self, results: Any, total_samples: int
    ) -> EvalResult:
        correct = 0
        total_score = 0.0
        for test_result in results.test_results:
            for metric_data in test_result.metrics_data:
                if metric_data.score == 1.0:
                    correct += 1
                total_score += metric_data.score
        incorrect = total_samples - correct
        accuracy_percentage = (correct / total_samples * 100) if total_samples > 0 else 0.0

        eval_result = EvalResult(
            model_name=self._get_model_name(),
            total=total_samples,
            correct=correct,
            incorrect=incorrect,
            avg_comprehensiveness=accuracy_percentage,
        )

        logger.info(
            f"Evaluation complete: {correct}/{total_samples} correct "
            f"({accuracy_percentage:.2f}%)"
        )

        return eval_result

    def _get_model_name(self) -> str:
        try:
            if hasattr(self.llm_model, "model_config"):
                return str(self.llm_model.model_config.model_name)
            return "unknown_model"
        except Exception:
            return "unknown_model"
