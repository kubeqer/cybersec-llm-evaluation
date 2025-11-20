from loguru import logger

from src.data.phishing.phishing_emails_dataloader import PhishingEmailsDataLoader
from src.data.phishing.phishing_website_dataloader import PhishingWebsiteDataLoader
from src.data.qa.cyberbench_dataloader import CyberBenchDataLoader
from src.data.qa.secbench_dataloader import SecBenchDataLoader
from src.data.vulnerable_code.bigvul_dataloader import BigVulDataLoader
from src.llm.schema import EvalType


def load_datasets():
    logger.info("Loading Datasets")
    datasets = {}
    logger.info("Phishing Emails Dataset")
    try:
        logger.info("Loading Phishing Emails Dataset...")
        loader = PhishingEmailsDataLoader()
        data = loader.load()
        datasets["phishing_emails"] = {
            "data": data,
            "eval_type": EvalType.PHISHING_DETECTION,
            "name": "Phishing Emails",
        }
        logger.info(f"Loaded {len(data)} phishing email samples")
    except Exception as e:
        logger.error(f"Failed to load Phishing Emails Dataset: {e}")
    logger.info("Phishing Website Dataset")
    try:
        logger.info("Loading Phishing Website Dataset...")
        loader = PhishingWebsiteDataLoader()
        data = loader.load()
        datasets["phishing_websites"] = {
            "data": data,
            "eval_type": EvalType.PHISHING_DETECTION,
            "name": "Phishing Websites",
        }
        logger.info(f"Loaded {len(data)} phishing website samples")
    except Exception as e:
        logger.error(f"Failed to load Phishing Website Dataset: {e}")
    logger.info("BigVul Code Vulnerability Dataset")
    try:
        logger.info("Loading BigVul (Code Vulnerability) Dataset...")
        loader = BigVulDataLoader()
        data = loader.load()
        datasets["bigvul"] = {
            "data": data,
            "eval_type": EvalType.CODE_SECURITY,
            "name": "BigVul Code Vulnerabilities",
        }
        logger.info(f"Loaded {len(data)} code vulnerability samples")
    except Exception as e:
        logger.error(f"Failed to load BigVul Dataset: {e}")
    logger.info("CyberBench Q&A Dataset")
    try:
        logger.info("Loading CyberBench Q&A Dataset...")
        loader = CyberBenchDataLoader()
        data = loader.load()
        datasets["cyberbench"] = {
            "data": data,
            "eval_type": EvalType.CYBERSECURITY_MCQ,
            "name": "CyberBench Q&A",
        }
        logger.info(f"Loaded {len(data)} CyberBench Q&A samples")
    except Exception as e:
        logger.error(f"Failed to load CyberBench Dataset: {e}")
    logger.info("SecBench Q&A Dataset")
    try:
        logger.info("Loading SecBench Q&A Dataset...")
        loader = SecBenchDataLoader()
        data = loader.load()
        datasets["secbench"] = {
            "data": data,
            "eval_type": EvalType.CYBERSECURITY_MCQ,
            "name": "SecBench Q&A",
        }
        logger.info(f"Loaded {len(data)} SecBench Q&A samples")
    except Exception as e:
        logger.error(f"Failed to load SecBench Dataset: {e}")
    logger.info(f"Total datasets loaded: {len(datasets)}")
    return datasets
