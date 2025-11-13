from concurrent.futures import ThreadPoolExecutor, as_completed

from loguru import logger

from src.data.schema import InputAnswerDict
from src.evaluation.schema import EvalResult
from src.llm.schema import EvalType


class BatchEvaluator:
    def __init__(self, llm_models: list[object], eval_type: EvalType):
        self.llm_models = llm_models
        self.eval_type = eval_type
        logger.info(
            f"Initialized MultiProcessBatchEvaluator with {len(llm_models)} models"
        )

    @staticmethod
    def _evaluate_single_model(
        model,
        data: list[InputAnswerDict],
        eval_type: EvalType,
        max_samples: int | None,
    ) -> EvalResult:
        try:
            from src.evaluation.evaluator import LLMEvaluator

            evaluator = LLMEvaluator(llm_model=model, eval_type=eval_type)
            logger.info(
                f"Starting evaluation for model: {model.model_config.model_name}"
            )
            result: EvalResult = evaluator.evaluate(data=data, max_samples=max_samples)
            logger.info(
                f"Completed evaluation for model: {model.model_config.model_name}"
            )
            return result
        except Exception as e:
            logger.error(
                f"Evaluation failed for model: {model.model_config.model_name} - {e}"
            )
            raise

    def evaluate_all(
        self,
        data: list[InputAnswerDict],
        max_samples: int | None = None,
        max_workers: int | None = None,
    ) -> list[EvalResult]:
        if max_workers is None:
            max_workers = len(self.llm_models)
        logger.info(f"Starting evaluation with {max_workers} parallel threads")
        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for idx, model in enumerate(self.llm_models):
                future = executor.submit(
                    self._evaluate_single_model,
                    model,
                    data,
                    self.eval_type,
                    max_samples,
                )
                futures[future] = (idx, model)
                logger.info(
                    f"Submitted model {idx + 1}/{len(self.llm_models)} for evaluation"
                )

            for future in as_completed(futures):
                idx, model = futures[future]

                try:
                    result = future.result()
                    results.append(result)
                    logger.info(
                        f"✓ Model {idx + 1}/{len(self.llm_models)} "
                        f"completed: {result.correct}/{result.total} correct "
                        f"({result.avg_comprehensiveness:.2f}%)"
                    )
                except Exception as e:
                    logger.error(f"Model {idx + 1}/{len(self.llm_models)} failed: {e}")

        logger.info(
            f"Completed {len(results)}/{len(self.llm_models)} model evaluations"
        )
        return results
