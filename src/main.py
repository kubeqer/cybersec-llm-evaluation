from datetime import datetime
from loguru import logger
from src.core.logging_setup import logging_setup
from src.pipeline.init_models import init_llms
from src.pipeline.load_datasets import load_datasets
from src.pipeline.results import print_summary, save_results
from src.pipeline.run_eval import run_evals


def main():
    logging_setup(level="DEBUG")
    try:
        models = init_llms()
        if not models:
            logger.error("No models were successfully initialized. Exiting.")
            return
        datasets = load_datasets()
        if not datasets:
            logger.error("No datasets were successfully loaded. Exiting.")
            return
        logger.info("EVALUATION CONFIGURATION")
        logger.info(f"Total Models: {len(models)}")
        logger.info(f"Total Datasets: {len(datasets)}")
        logger.info(
            f"Total Evaluations: {len(models)} models * {len(datasets)} datasets = {len(models) * len(datasets)} evaluations"
        )
        results = run_evals(
            models=models,
            datasets=datasets,
            max_samples=150,
            max_workers=None,
        )
        results_file = save_results(results, datetime.now().strftime("%Y%m%d_%H%M%S"))
        print_summary(results)
        logger.info("EVALUATION COMPLETED SUCCESSFULLY!")
        logger.info(f"Total Models Evaluated: {len(models)}")
        logger.info(f"Total Datasets Evaluated: {len(datasets)}")
        logger.info(f"Results saved to: {results_file}")
    except Exception as e:
        logger.error(f"Evaluation pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
