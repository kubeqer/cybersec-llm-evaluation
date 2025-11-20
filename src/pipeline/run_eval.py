from datetime import datetime

from loguru import logger

from src.evaluation.batch_evaluator import BatchEvaluator
from src.pipeline.results import save_results


def run_evals(models, datasets, max_samples=None, max_workers=None):
    logger.info("Starting Evaluations")
    all_results = {}
    for dataset_key, dataset_info in datasets.items():
        logger.info(f"Evaluating Dataset: {dataset_info['name']}")
        data = dataset_info["data"]
        eval_type = dataset_info["eval_type"]
        logger.info(f"Dataset size: {len(data)} samples")
        if max_samples:
            logger.info(f"Max samples to evaluate: {max_samples}")
        evaluator = BatchEvaluator(
            llm_models=models,
            eval_type=eval_type,
        )
        try:
            results = evaluator.evaluate_all(
                data=data,
                max_samples=max_samples,
                max_workers=max_workers,
            )
            all_results[dataset_key] = {
                "dataset_name": dataset_info["name"],
                "eval_type": eval_type.value,
                "results": results,
            }
            save_results(all_results, datetime.now().strftime("%Y%m%d_%H%M%S"))
            logger.info(f"Completed evaluation for {dataset_info['name']}")
        except Exception as e:
            logger.error(f"Failed evaluation for {dataset_info['name']}: {e}")
    return all_results
