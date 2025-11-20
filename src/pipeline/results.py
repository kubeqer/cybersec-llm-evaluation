import json

from loguru import logger

from src.core.paths import RESULTS_DIR


def save_results(results: dict, timestamp: str):
    logger.info("Saving Results")
    results_file = RESULTS_DIR / f"evaluation_results_{timestamp}.json"
    serializable_results = {}
    for dataset_key, dataset_results in results.items():
        serializable_results[dataset_key] = {
            "dataset_name": dataset_results["dataset_name"],
            "eval_type": dataset_results["eval_type"],
            "results": [
                {
                    "model_name": r.model_name,
                    "total": r.total,
                    "correct": r.correct,
                    "incorrect": r.incorrect,
                    "accuracy": r.avg_comprehensiveness,
                    "true_positives": r.true_positives,
                    "false_positives": r.false_positives,
                    "true_negatives": r.true_negatives,
                    "false_negatives": r.false_negatives,
                    "precision": r.precision,
                    "recall": r.recall,
                    "f1_score": r.f1_score,
                }
                for r in dataset_results["results"]
            ],
        }

    with open(results_file, "w") as f:
        json.dump(serializable_results, f, indent=2)

    logger.info(f"Results saved to: {results_file}")
    return results_file


def print_summary(results: dict):
    logger.info("EVALUATION SUMMARY")
    for _, dataset_results in results.items():
        logger.info(
            f"\n{dataset_results['dataset_name']} ({dataset_results['eval_type']}):"
        )
        for result in dataset_results["results"]:
            logger.info(f"\n  Model: {result.model_name}")
            logger.info(f"    Accuracy:  {result.avg_comprehensiveness:.2f}%")
            logger.info(f"    Precision: {result.precision:.2f}%")
            logger.info(f"    Recall:    {result.recall:.2f}%")
            logger.info(f"    F1 Score:  {result.f1_score:.2f}%")
            logger.info(f"    Correct:   {result.correct}/{result.total}")
            logger.info(
                f"    Confusion Matrix: TP={result.true_positives}, "
                f"FP={result.false_positives}, TN={result.true_negatives}, "
                f"FN={result.false_negatives}"
            )
