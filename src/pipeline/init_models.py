from loguru import logger

from src.llm.cloud.anthropic.claude_anthropic import ClaudeAnthropic
from src.llm.cloud.anthropic.schema import AnthropicConfig
from src.llm.cloud.google.google_gemini import GoogleGemini
from src.llm.cloud.google.schema import GoogleConfig
from src.llm.cloud.openai.openai_gpt import OpenAIGPT
from src.llm.cloud.openai.schema import OpenAIConfig
from src.llm.cloud.xai.schema import GrokConfig
from src.llm.cloud.xai.xai_grok import Grok
from src.llm.on_premise.hf import HF
from src.llm.on_premise.schema import HFConfig


def init_llms():
    logger.info("Initializing LLM models...")
    models = []
    logger.info("Anthropic Claude Models")
    try:
        models.append(
            ClaudeAnthropic(
                model_config=AnthropicConfig(
                    model_name="claude-sonnet-4-5",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Claude Sonnet 4.5")
    except Exception as e:
        logger.warning(f"Failed to initialize Claude Sonnet 4.0: {e}")
    logger.info("Google Gemini Models")
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
        logger.info("Initialized Gemini 3 Pro")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini 3 Pro: {e}")
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
        logger.info("Initialized Gemini 2.5 Pro")
    except Exception as e:
        logger.warning(f"Failed to initialize Gemini 2.5 Pro: {e}")
    logger.info("\nOpenAI GPT Models ---")
    try:
        models.append(
            OpenAIGPT(
                model_config=OpenAIConfig(
                    model_name="gpt-5.1",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized GPT-5.1")
    except Exception as e:
        logger.warning(f"Failed to initialize GPT-5.1: {e}")
    try:
        models.append(
            OpenAIGPT(
                model_config=OpenAIConfig(
                    model_name="gpt-5.1-codex",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized GPT-5.1 Codex")
    except Exception as e:
        logger.warning(f"Failed to initialize GPT-5.1 Codex: {e}")
    try:
        models.append(
            OpenAIGPT(
                model_config=OpenAIConfig(
                    model_name="gpt-5-nano",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("✓ Initialized GPT-5 Nano")
    except Exception as e:
        logger.warning(f"✗ Failed to initialize GPT-5 Nano: {e}")
    logger.info("xAI Grok Models")
    try:
        models.append(
            Grok(
                model_config=GrokConfig(
                    model_name="grok-4-fast-reasoning",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Grok-4 Fast Reasoning")
    except Exception as e:
        logger.warning(f"Failed to initialize Grok-4 Fast Reasoning: {e}")
    try:
        models.append(
            Grok(
                model_config=GrokConfig(
                    model_name="grok-code-fast-1",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Grok Code Fast 1")
    except Exception as e:
        logger.warning(f"Failed to initialize Grok Code Fast: {e}")
    logger.info("Hugging Face Models")
    try:
        models.append(
            HF(
                model_config=HFConfig(
                    model_name="deepseek-ai/DeepSeek-V3.1",
                    provider="auto",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized DeepSeek V3.1")
    except Exception as e:
        logger.warning(f"Failed to initialize DeepSeek V3.1: {e}")
    try:
        models.append(
            HF(
                model_config=HFConfig(
                    model_name="deepseek-ai/DeepSeek-V3.2-Exp",
                    provider="auto",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Deepseek V3.2 EXP")
    except Exception as e:
        logger.warning(f"Failed to initialize Deepseek V3.2 EXP: {e}")
    try:
        models.append(
            HF(
                model_config=HFConfig(
                    model_name="Qwen/Qwen3-Coder-30B-A3B-Instruct",
                    provider="auto",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Qwen 3 Coder Instruct")
    except Exception as e:
        logger.warning(f"Failed to initialize Qwen 3 Coder Instruct: {e}")
    try:
        models.append(
            HF(
                model_config=HFConfig(
                    model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct",
                    provider="auto",
                    max_tokens=2048,
                    temperature=0.0,
                )
            )
        )
        logger.info("Initialized Llama 4 Maverick Instruct")
    except Exception as e:
        logger.warning(f"Failed to initialize Llama 4 Maverick Instruct: {e}")
    logger.info(f"Total models initialized: {len(models)}")
    return models
