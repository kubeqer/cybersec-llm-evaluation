from google import genai
from google.genai import types
from loguru import logger

from src.core.decorators.log_calls import log_calls
from src.core.decorators.retry import retry
from src.core.settings.settings import settings
from src.llm.cloud.google.schema import GoogleConfig
from src.llm.schema import EvalType
from src.llm.system_prompts import SYSTEM_PROMPT


class GoogleGemini:
    def __init__(
        self,
        model_config: GoogleConfig,
    ):
        self.model_config: GoogleConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = genai.Client(api_key=settings.google_apikey)

    @log_calls(level="INFO")
    @retry(max_retries=50, delay_seconds=20)
    def generate(self, message: str, eval_type: EvalType) -> str | None:
        completion = self.client.models.generate_content(
            model=self.model_config.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt.get(eval_type.value),
            ),
        )
        logger.info(completion.text)
        return completion.text
