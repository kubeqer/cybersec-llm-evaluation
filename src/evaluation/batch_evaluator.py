import multiprocessing as mp
import pickle
from concurrent.futures import ProcessPoolExecutor, as_completed

from loguru import logger

from src.data.schema import InputAnswerDict
from src.evaluation.schema import EvalResult
from src.llm.schema import EvalType


class MultiProcessBatchEvaluator:
    def __init__(self, llm_models: list[object], eval_type: EvalType):
        self.llm_models = llm_models
        self.eval_type = eval_type
        logger.info(
            f"Initialized MultiProcessBatchEvaluator with {len(llm_models)} models"
        )

    @staticmethod
    def _evaluate_single_model(
        model_pickle: bytes,
        data: list[InputAnswerDict],
        eval_type: EvalType,
        max_samples: int | None,
    ) -> EvalResult:
        try:
            from src.evaluation.evaluator import LLMEvaluator

            model = pickle.loads(model_pickle)
            evaluator = LLMEvaluator(llm_model=model, eval_type=eval_type)
            logger.info(f"Process {mp.current_process().name}: Starting evaluation")
            result: EvalResult = evaluator.evaluate(data=data, max_samples=max_samples)
            logger.info(f"Process {mp.current_process().name}: Completed evaluation")
            return result
        except Exception as e:
            logger.error(
                f"Process {mp.current_process().name}: Evaluation failed - {e}"
            )
            raise

    def evaluate_all(
        self,
        data: list[InputAnswerDict],
        max_samples: int | None = None,
        max_workers: int | None = None,
    ) -> list[EvalResult]:
        if max_workers is None:
            max_workers = min(len(self.llm_models), mp.cpu_count())
        logger.info(f"Starting evaluation with {max_workers} parallel processes")
        results = []
        pickled_models = []
        for idx, model in enumerate(self.llm_models):
            try:
                pickled_model = pickle.dumps(model)
                pickled_models.append(pickled_model)
                logger.info(f"Serialized model {idx + 1}/{len(self.llm_models)}")
            except Exception as e:
                logger.error(f"Failed to serialize model {idx + 1}: {e}")
                raise
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for idx, pickled_model in enumerate(pickled_models):
                future = executor.submit(
                    self._evaluate_single_model,
                    pickled_model,
                    data,
                    self.eval_type,
                    max_samples,
                )
                futures[future] = idx
                logger.info(
                    f"Submitted model {idx + 1}/{len(self.llm_models)} for evaluation"
                )
            for future in as_completed(futures):
                idx = futures[future]

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
