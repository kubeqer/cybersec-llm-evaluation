import json
from datetime import datetime

from loguru import logger

from src.core.logging_setup import logging_setup
from src.core.paths import RESULTS_DIR
from src.data.vulnerable_code.bigvul_dataloader import BigVulDataLoader
from src.data.phishing.phishing_emails_dataloader import PhishingEmailsDataLoader
from src.data.phishing.phishing_website_dataloader import PhishingWebsiteDataLoader
from src.data.qa.cyberbench_dataloader import CyberBenchDataLoader
from src.data.qa.secbench_dataloader import SecBenchDataLoader
from src.evaluation.batch_evaluator import BatchEvaluator
from src.llm.cloud.google.google_gemini import GoogleGemini
from src.llm.cloud.google.schema import GoogleConfig
from src.llm.cloud.anthropic.claude_anthropic import ClaudeAnthropic
from src.llm.cloud.anthropic.schema import AnthropicConfig
from src.llm.cloud.openai.openai_gpt import OpenAIGPT
from src.llm.cloud.openai.schema import OpenAIConfig
from src.llm.cloud.xai.schema import GrokConfig
from src.llm.cloud.xai.xai_grok import Grok
from src.llm.on_premise.hf import HF
from src.llm.on_premise.schema import HFConfig
from src.llm.schema import EvalType


def initialize_models():
    """Initialize all LLM models for evaluation"""
    logger.info("Initializing LLM models...")

    models = []
    #
    # # Anthropic Claude models
    # try:
    #     models.append(
    #         ClaudeAnthropic(
    #             model_config=AnthropicConfig(
    #                 model_name="claude-sonnet-4-0",
    #                 max_tokens=1,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Claude Sonnet 4.0")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Claude Sonnet 4.0: {e}")
    #
    # try:
    #     models.append(
    #         ClaudeAnthropic(
    #             model_config=AnthropicConfig(
    #                 model_name="claude-opus-4-1",
    #                 max_tokens=1,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Claude Opus 4.1")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Claude Opus 4.1: {e}")
    #
    # # Google Gemini models
    try:
        models.append(
            GoogleGemini(
                model_config=GoogleConfig(
                    model_name="gemini-2.5-pro",
                    max_tokens=1,
                    temperature=0.0,
                )
            )
        )
        logger.info("✓ Initialized Gemini 2.5 Pro")
    except Exception as e:
        logger.warning(f"✗ Failed to initialize Gemini 2.5 Pro: {e}")

    try:
        models.append(
            GoogleGemini(
                model_config=GoogleConfig(
                    model_name="gemini-2.5-flash",
                    max_tokens=1,
                    temperature=0.0,
                )
            )
        )
        logger.info("✓ Initialized Gemini 2.5 Flash")
    except Exception as e:
        logger.warning(f"✗ Failed to initialize Gemini 2.5 Flash: {e}")

    # # OpenAI GPT models
    # try:
    #     models.append(
    #         OpenAIGPT(
    #             model_config=OpenAIConfig(
    #                 model_name="gpt-5",
    #                 max_tokens=1,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized GPT-5")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize GPT-5: {e}")
    #
    # # Hugging Face models (examples - add more as needed)
    # try:
    #     models.append(
    #         HF(
    #             model_config=HFConfig(
    #                 model_name="meta-llama/Llama-3.3-70B-Instruct",
    #                 provider="auto",
    #                 max_tokens=1,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Llama 3.3 70B")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Llama 3.3 70B: {e}")

    logger.info(f"Total models initialized: {len(models)}")
    return models


def load_datasets():
    """Load all available datasets"""
    logger.info("\n" + "=" * 80)
    logger.info("Loading Datasets")
    logger.info("=" * 80)

    datasets = {}

    # # Phishing Emails Dataset
    # try:
    #     logger.info("Loading Phishing Emails Dataset...")
    #     loader = PhishingEmailsDataLoader()
    #     data = loader.load()
    #     datasets["phishing_emails"] = {
    #         "data": data,
    #         "eval_type": EvalType.PHISHING_DETECTION,
    #         "name": "Phishing Emails",
    #     }
    #     logger.info(f"✓ Loaded {len(data)} phishing email samples")
    # except Exception as e:
    #     logger.error(f"✗ Failed to load Phishing Emails Dataset: {e}")

    # Phishing Website Dataset
    # try:
    #     logger.info("Loading Phishing Website Dataset...")
    #     loader = PhishingWebsiteDataLoader()
    #     data = loader.load()
    #     datasets["phishing_websites"] = {
    #         "data": data,
    #         "eval_type": EvalType.PHISHING_DETECTION,
    #         "name": "Phishing Websites",
    #     }
    #     logger.info(f"✓ Loaded {len(data)} phishing website samples")
    # except Exception as e:
    #     logger.error(f"✗ Failed to load Phishing Website Dataset: {e}")

    # BigVul Dataset
    try:
        logger.info("Loading BigVul (Code Vulnerability) Dataset...")
        loader = BigVulDataLoader()
        data = loader.load()
        datasets["bigvul"] = {
            "data": data,
            "eval_type": EvalType.CODE_SECURITY,
            "name": "BigVul Code Vulnerabilities",
        }
        logger.info(f"✓ Loaded {len(data)} code vulnerability samples")
    except Exception as e:
        logger.error(f"✗ Failed to load BigVul Dataset: {e}")

    logger.info(f"\nTotal datasets loaded: {len(datasets)}")
    return datasets


def run_evaluations(models, datasets, max_samples=None, max_workers=None):
    """Run evaluations for all models on all datasets"""
    logger.info("\n" + "=" * 80)
    logger.info("Starting Evaluations")
    logger.info("=" * 80)

    all_results = {}

    for dataset_key, dataset_info in datasets.items():
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Evaluating Dataset: {dataset_info['name']}")
        logger.info(f"{'=' * 80}")

        data = dataset_info["data"]
        eval_type = dataset_info["eval_type"]

        if not data:
            logger.warning(f"Skipping {dataset_info['name']} - no data available")
            continue

        logger.info(f"Dataset size: {len(data)} samples")
        if max_samples:
            logger.info(f"Max samples to evaluate: {max_samples}")

        # Create batch evaluator
        evaluator = BatchEvaluator(
            llm_models=models,
            eval_type=eval_type,
        )

        # Run evaluation
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
            logger.info(f"✓ Completed evaluation for {dataset_info['name']}")
        except Exception as e:
            logger.error(f"✗ Failed evaluation for {dataset_info['name']}: {e}")

    return all_results


def save_results(results: dict, timestamp: str):
    """Save evaluation results to JSON file"""
    logger.info("\n" + "=" * 80)
    logger.info("Saving Results")
    logger.info("=" * 80)

    results_file = RESULTS_DIR / f"evaluation_results_{timestamp}.json"

    # Convert EvalResult objects to dictionaries
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

    logger.info(f"✓ Results saved to: {results_file}")
    return results_file


def print_summary(results: dict):
    """Print a summary of evaluation results"""
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATION SUMMARY")
    logger.info("=" * 80)

    for dataset_key, dataset_results in results.items():
        logger.info(
            f"\n{dataset_results['dataset_name']} ({dataset_results['eval_type']}):"
        )
        logger.info("-" * 80)

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


def initialize_all_models():
    logger.info("=" * 80)
    logger.info("Initializing LLM models...")
    logger.info("=" * 80)

    models = []

    # Anthropic Claude models
    # logger.info("\n--- Anthropic Claude Models ---")
    # try:
    #     models.append(
    #         ClaudeAnthropic(
    #             model_config=AnthropicConfig(
    #                 model_name="claude-sonnet-4-5",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Claude Sonnet 4.5")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Claude Sonnet 4.0: {e}")

    # Google Gemini models
    logger.info("\n--- Google Gemini Models ---")
    try:
        models.append(
            GoogleGemini(
                model_config=GoogleConfig(
                    model_name="gemini-3-pro-preview",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("✓ Initialized Gemini 3 Pro")
    except Exception as e:
        logger.warning(f"✗ Failed to initialize Gemini 3 Pro: {e}")

    try:
        models.append(
            GoogleGemini(
                model_config=GoogleConfig(
                    model_name="gemini-2.5-pro",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("✓ Initialized Gemini 2.5 Pro")
    except Exception as e:
        logger.warning(f"✗ Failed to initialize Gemini 2.5 Pro: {e}")

    # OpenAI GPT models
    # logger.info("\n--- OpenAI GPT Models ---")
    #
    # # GPT-5.1
    # try:
    #     models.append(
    #         OpenAIGPT(
    #             model_config=OpenAIConfig(
    #                 model_name="gpt-5.1",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized GPT-5.1")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize GPT-5.1: {e}")
    #
    # # GPT-5.1 Codex
    # try:
    #     models.append(
    #         OpenAIGPT(
    #             model_config=OpenAIConfig(
    #                 model_name="gpt-5.1-codex",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized GPT-5.1 Codex")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize GPT-5.1 Codex: {e}")
    #
    # # GPT-5 Nano
    # try:
    #     models.append(
    #         OpenAIGPT(
    #             model_config=OpenAIConfig(
    #                 model_name="gpt-5-nano",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized GPT-5 Nano")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize GPT-5 Nano: {e}")
    # # xAI Grok models
    # logger.info("\n--- xAI Grok Models ---")
    #
    # # Grok-4 Fast Reasoning (most powerful current model)
    # try:
    #     models.append(
    #         Grok(
    #             model_config=GrokConfig(
    #                 model_name="grok-4-fast-reasoning",
    #                 max_tokens=8192,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Grok-4 Fast Reasoning")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Grok-4 Fast Reasoning: {e}")
    #
    # # Grok Code Fast (optimized for code generation & reasoning)
    # try:
    #     models.append(
    #         Grok(
    #             model_config=GrokConfig(
    #                 model_name="grok-code-fast-1",
    #                 max_tokens=8192,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Grok Code Fast 1")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Grok Code Fast: {e}")

    # Hugging Face models (examples with popular cybersecurity-relevant models)
    logger.info("\n--- Hugging Face Models ---")
    # try:
    #     models.append(
    #         HF(
    #             model_config=HFConfig(
    #                 model_name="meta-llama/Llama-3.3-70B-Instruct",
    #                 provider="auto",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Llama 3.3 70B Instruct")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Llama 3.3 70B: {e}")
    #
    # try:
    #     models.append(
    #         HF(
    #             model_config=HFConfig(
    #                 model_name="Qwen/Qwen2.5-72B-Instruct",
    #                 provider="auto",
    #                 max_tokens=2048,
    #                 temperature=0.0,
    #             )
    #         )
    #     )
    #     logger.info("✓ Initialized Qwen 2.5 72B Instruct")
    # except Exception as e:
    #     logger.warning(f"✗ Failed to initialize Qwen 2.5 72B: {e}")

    logger.info(f"\n{'=' * 80}")
    logger.info(f"Total models initialized: {len(models)}")
    logger.info(f"{'=' * 80}")
    return models


def load_all_datasets():
    """Load ALL available datasets for comprehensive evaluation"""
    logger.info("\n" + "=" * 80)
    logger.info("Loading ALL Datasets")
    logger.info("=" * 80)

    datasets = {}

    # Phishing Emails Dataset
    logger.info("\n--- Phishing Emails Dataset ---")
    try:
        logger.info("Loading Phishing Emails Dataset...")
        loader = PhishingEmailsDataLoader()
        data = loader.load()
        datasets["phishing_emails"] = {
            "data": data,
            "eval_type": EvalType.PHISHING_DETECTION,
            "name": "Phishing Emails",
        }
        logger.info(f"✓ Loaded {len(data)} phishing email samples")
    except Exception as e:
        logger.error(f"✗ Failed to load Phishing Emails Dataset: {e}")

    # # Phishing Website Dataset
    logger.info("\n--- Phishing Website Dataset ---")
    try:
        logger.info("Loading Phishing Website Dataset...")
        loader = PhishingWebsiteDataLoader()
        data = loader.load()
        datasets["phishing_websites"] = {
            "data": data,
            "eval_type": EvalType.PHISHING_DETECTION,
            "name": "Phishing Websites",
        }
        logger.info(f"✓ Loaded {len(data)} phishing website samples")
    except Exception as e:
        logger.error(f"✗ Failed to load Phishing Website Dataset: {e}")
    logger.info("\n--- BigVul Code Vulnerability Dataset ---")
    try:
        logger.info("Loading BigVul (Code Vulnerability) Dataset...")
        loader = BigVulDataLoader()
        data = loader.load()
        datasets["bigvul"] = {
            "data": data,
            "eval_type": EvalType.CODE_SECURITY,
            "name": "BigVul Code Vulnerabilities",
        }
        logger.info(f"✓ Loaded {len(data)} code vulnerability samples")
    except Exception as e:
        logger.error(f"✗ Failed to load BigVul Dataset: {e}")

    # CyberBench Q&A Dataset
    logger.info("\n--- CyberBench Q&A Dataset ---")
    try:
        logger.info("Loading CyberBench Q&A Dataset...")
        loader = CyberBenchDataLoader()
        data = loader.load()
        datasets["cyberbench"] = {
            "data": data,
            "eval_type": EvalType.CYBERSECURITY_MCQ,
            "name": "CyberBench Q&A",
        }
        logger.info(f"✓ Loaded {len(data)} CyberBench Q&A samples")
    except Exception as e:
        logger.error(f"✗ Failed to load CyberBench Dataset: {e}")
    logger.info("\n--- SecBench Q&A Dataset ---")
    try:
        logger.info("Loading SecBench Q&A Dataset...")
        loader = SecBenchDataLoader()
        data = loader.load()
        datasets["secbench"] = {
            "data": data,
            "eval_type": EvalType.CYBERSECURITY_MCQ,
            "name": "SecBench Q&A",
        }
        logger.info(f"✓ Loaded {len(data)} SecBench Q&A samples")
    except Exception as e:
        logger.error(f"✗ Failed to load SecBench Dataset: {e}")

    logger.info(f"\n{'=' * 80}")
    logger.info(f"Total datasets loaded: {len(datasets)}")
    logger.info(f"{'=' * 80}")
    return datasets


def main_comprehensive():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Setup logging
    logging_setup()

    logger.info("\n" + "=" * 80)
    logger.info("COMPREHENSIVE LLM CYBERSECURITY EVALUATION PIPELINE")
    logger.info("=" * 80)
    logger.info("This will test ALL datasets with ALL available LLM models")
    logger.info("=" * 80)

    try:
        # Initialize ALL models
        models = initialize_all_models()

        if not models:
            logger.error("No models were successfully initialized. Exiting.")
            return

        # Load ALL datasets
        datasets = load_all_datasets()

        if not datasets:
            logger.error("No datasets were successfully loaded. Exiting.")
            return

        # Run comprehensive evaluations
        logger.info("\n" + "=" * 80)
        logger.info("EVALUATION CONFIGURATION")
        logger.info("=" * 80)
        logger.info(f"Total Models: {len(models)}")
        logger.info(f"Total Datasets: {len(datasets)}")
        logger.info(
            f"Total Evaluations: {len(models)} models × {len(datasets)} datasets = {len(models) * len(datasets)} evaluations"
        )
        logger.info("Max samples per dataset: 1000 (configurable)")
        logger.info("Parallelism: Using all available CPU cores")
        logger.info("=" * 80)

        results = run_evaluations(
            models=models,
            datasets=datasets,
            max_samples=150,
            max_workers=None,
        )
        results_file = save_results(results, timestamp)
        print_summary(results)
        logger.info("\n" + "=" * 80)
        logger.info("COMPREHENSIVE EVALUATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)
        logger.info(f"Total Models Evaluated: {len(models)}")
        logger.info(f"Total Datasets Evaluated: {len(datasets)}")
        logger.info(f"Results saved to: {results_file}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Comprehensive evaluation pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main_comprehensive()
