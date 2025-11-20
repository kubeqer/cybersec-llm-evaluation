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
        executor = ThreadPoolExecutor(max_workers=max_workers)
        try:
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

            logger.info("All models submitted, waiting for completion...")

            for future in as_completed(futures):
                idx, model = futures[future]

                try:
                    result = future.result(timeout=600)
                    results.append(result)
                    logger.info(
                        f"Model {idx + 1}/{len(self.llm_models)} "
                        f"completed: {result.correct}/{result.total} correct "
                        f"({result.avg_comprehensiveness:.2f}%)"
                    )
                except TimeoutError:
                    logger.error(
                        f"Model {idx + 1}/{len(self.llm_models)} timed out after 600s"
                    )
                except Exception as e:
                    logger.error(f"Model {idx + 1}/{len(self.llm_models)} failed: {e}")

            logger.info("All futures completed, shutting down executor...")
        finally:
            executor.shutdown(wait=False, cancel_futures=False)
            logger.info("Executor shutdown complete")

        logger.info(
            f"Completed {len(results)}/{len(self.llm_models)} model evaluations"
        )
        return results
