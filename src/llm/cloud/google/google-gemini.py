from google import genai
from google.genai import types

from src.core.consts import SYSTEM_PROMPT
from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.core.settings.settings import settings
from src.llm.cloud.google.schema import GoogleConfig
from src.llm.schema import EvalType


class GoogleGemini:
    def __init__(
        self,
        model_config: GoogleConfig,
    ):
        self.model_config: GoogleConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = genai.Client(api_key=settings.google_apikey)

    @error_handling
    @log_calls
    def generate(self, message: str, eval_type: EvalType) -> str:
        generation_config = types.GenerationConfig(
            max_output_tokens=self.model_config.max_tokens,
            temperature=self.model_config.temperature,
            top_p=self.model_config.top_p,
            top_k=self.model_config.top_k,
        )
        completion = self.client.models.generate_content(
            model=self.model_config.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt.get(eval_type.value),
                **generation_config.model_dump(),
            ),
        )
        return completion.text if completion.text else ""
