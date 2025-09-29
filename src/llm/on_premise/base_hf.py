from huggingface_hub import InferenceClient

from src.core.decorators.error_handling import error_handling
from src.core.decorators.log_calls import log_calls
from src.core.settings.settings import settings
from src.llm.consts import SYSTEM_PROMPT
from src.llm.on_premise.schema import HFConfig
from src.llm.schema import EvalType


class BaseHF:
    def __init__(
        self,
        model_config: HFConfig,
    ):
        self.model_config: HFConfig = model_config
        self.system_prompt: dict[str, str] = SYSTEM_PROMPT
        self.client = InferenceClient(
            provider=self.model_config.provider,
            timeout=self.model_config.timeout,
            token=settings.hf_token,
        )

    @log_calls(level="INFO")
    @error_handling(default=[], reraise=True)
    def generate(self, message: str, eval_type: EvalType) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_config.model_name,
            messages=[
                {
                    "role": "assistant",
                    "content": self.system_prompt.get(
                        eval_type.value
                    ),  # todo: check if it will work correctly on all the models i will use # noqa: E501
                },
                {"role": "user", "content": message},
            ],
            **self.model_config.to_generation_params(),
        )
        return str(completion.choices[0].message)
