import anthropic

from src.core.consts import SYSTEM_PROMPT
from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.core.settings.settings import settings
from src.llm.cloud.anthropic.schema import AnthropicConfig
from src.llm.schema import EvalType


class ClaudeAnthropic:
    def __init__(
        self,
        model_config: AnthropicConfig,
    ):
        self.model_config: AnthropicConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = anthropic.Anthropic(auth_token=settings.anthropic_token)

    @error_handling
    @log_calls
    def generate(self, message: str, eval_type: EvalType) -> str:
        # noinspection PyTypeChecker
        completion = self.client.messages.create(
            model=self.model_config.model_name,  # type: ignore # third-party type issue
            system=self.system_prompt.get(eval_type.value),
            messages=[
                {"role": "user", "content": message},
            ],
            **self.model_config.to_generation_params(),
        )
        return str(completion.choices[0].message)
