from loguru import logger

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.data.schema import InputAnswerDict
from src.evaluation.evaluator import LLMEvaluator
from src.evaluation.schema import EvalResult
from src.llm.schema import EvalType


class BatchLLMEvaluator:
    def __init__(self, llm_models: list[object], eval_type: EvalType):
        self.llm_models = llm_models
        self.eval_type = eval_type
        logger.info(f"Initialized BatchLLMEvaluator with {len(llm_models)} models")

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def evaluate_all(
        self, data: list[InputAnswerDict], max_samples: int | None = None
    ) -> list[EvalResult]:
        results = []
        for idx, model in enumerate(self.llm_models):
            logger.info(f"Evaluating model {idx + 1}/{len(self.llm_models)}")
            evaluator = LLMEvaluator(llm_model=model, eval_type=self.eval_type)
            result = evaluator.evaluate(data=data, max_samples=max_samples)
            results.append(result)
        return results
