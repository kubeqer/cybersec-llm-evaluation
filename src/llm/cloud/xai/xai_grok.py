from xai_sdk import Client  # type: ignore
from xai_sdk.chat import system, user  # type: ignore

from src.core.decorators.log_calls import log_calls
from src.core.decorators.retry import retry
from src.core.settings.settings import settings
from src.llm.cloud.xai.schema import GrokConfig
from src.llm.schema import EvalType
from src.llm.system_prompts import SYSTEM_PROMPT


class Grok:
    def __init__(
        self,
        model_config: GrokConfig,
    ):
        self.model_config = model_config
        self.system_prompt: dict[EvalType, str] = SYSTEM_PROMPT
        self.client = Client(api_key=settings.xai_api_key)

    @log_calls(level="DEBUG", show_result=True)
    @log_calls(level="INFO")
    @retry(max_retries=15, delay_seconds=120)
    def generate(self, message: str, eval_type: EvalType) -> str:
        sys_prompt = self.system_prompt.get(eval_type, "")
        chat = self.client.chat.create(
            model=self.model_config.model_name,
            temperature=self.model_config.temperature,
            max_tokens=self.model_config.max_tokens,
        )
        chat.append(system(sys_prompt))
        chat.append(user(message))
        response = chat.sample()
        return str(response.content.strip())
