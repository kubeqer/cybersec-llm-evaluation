from openai import OpenAI

from src.core.consts import SYSTEM_PROMPT
from src.core.settings.settings import settings
from src.llm.cloud.openai.schema import OpenAIConfig
from src.llm.schema import EvalType


class OpenAIGPT:
    def __init__(
        self,
        model_config: OpenAIConfig,
    ):
        self.model_config: OpenAIConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = OpenAI(api_key=settings.openai_apikey)

    def generate(self, message: str, eval_type: EvalType) -> str:
        completion = self.client.responses.create(
            model=self.model_config.model_name,
            instructions=SYSTEM_PROMPT.get(eval_type.value),
            input=message,
        )
        return completion.output_text
