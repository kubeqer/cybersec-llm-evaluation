from google import genai
from google.genai import types

from src.core.settings.settings import settings
from src.llm.cloud.google.schema import GoogleConfig
from src.llm.consts import SYSTEM_PROMPT
from src.llm.schema import EvalType


class GoogleGemini:
    def __init__(
        self,
        model_config: GoogleConfig,
    ):
        self.model_config: GoogleConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = genai.Client(api_key=settings.google_apikey)

    def generate(self, message: str, eval_type: EvalType) -> str:
        completion = self.client.models.generate_content(
            model=self.model_config.model_name,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt.get(eval_type.value),
            ),
        )
        return completion.text if completion.text else ""
